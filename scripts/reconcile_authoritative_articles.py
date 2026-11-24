#!/usr/bin/env python3
"""Compare complete, selected open-access primary article checklist tables to legacy views."""
from __future__ import annotations

import argparse
from collections import Counter
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from xml.etree import ElementTree as ET

if __package__:
    from .source_xml import parse_xml
    from .classical_linguistic_nlp import compare as compare_linguistic, load_reference
    from .jats_checklist_structure import describe_table
    from .legacy_checklist_structure import parse_legacy_tasks
else:
    from source_xml import parse_xml
    from classical_linguistic_nlp import compare as compare_linguistic, load_reference
    from jats_checklist_structure import describe_table
    from legacy_checklist_structure import parse_legacy_tasks

MAX_BYTES = 8_000_000
ITEM_ID = re.compile(r"^[0-9]{1,3}[a-z]?$", re.I)
LICENCE = {
    "CC-BY-4.0": "creativecommons.org/licenses/by/4.0",
    "CC0-1.0": "creativecommons.org/publicdomain/zero/1.0",
}


def normalize(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).split())


def content(element: ET.Element | None) -> str:
    return normalize("".join(element.itertext())) if element is not None else ""


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_table(raw: bytes, spec: dict) -> dict:
    if not raw or len(raw) > MAX_BYTES:
        raise ValueError("empty or oversized article XML")
    checksum = hashlib.sha256(raw).hexdigest()
    if spec.get("source_sha256") and checksum != spec["source_sha256"]:
        raise ValueError("source checksum differs from pinned article")
    if spec.get("source_bytes") is not None and len(raw) != spec["source_bytes"]:
        raise ValueError("source length differs from pinned article")
    root = parse_xml(raw, MAX_BYTES)
    if root.tag != "article":
        raise ValueError("expected a primary JATS article")
    meta = root.find("./front/article-meta")
    if meta is None:
        raise ValueError("missing article identity")
    ids = {element.get("pub-id-type"): content(element)
           for element in meta.findall("article-id")}
    if ids.get("doi", "").lower() != spec["doi"].lower():
        raise ValueError("article DOI differs from selected edition")
    pmc = ids.get("pmc") or ids.get("pmcid")
    if pmc and pmc.upper().removeprefix("PMC") != spec["pmcid"].removeprefix("PMC"):
        raise ValueError("article PMCID differs from selected edition")
    if ids.get("pmid") and ids["pmid"] != spec["pmid"]:
        raise ValueError("article PMID differs from selected edition")
    licences = meta.findall("./permissions/license")
    licence_evidence = " ".join(
        content(node) + " " + " ".join(v for el in node.iter() for v in el.attrib.values())
        for node in licences
    ).lower()
    expected = LICENCE[spec["licence"]]
    if not re.search(r"https?://" + re.escape(expected) + r"(?:/|(?=[\s.,;]|$))", licence_evidence):
        raise ValueError("selected article licence not found in JATS permissions")
    # Table-local rights/third-party attribution need separate review, not inference.
    tables = [table for table in root.findall("./body//table-wrap")
              if content(table.find("label")).rstrip(".").casefold() == spec["table_label"].casefold()
              and spec["caption_contains"].casefold() in content(table.find("caption")).casefold()]
    if len(tables) != 1:
        raise ValueError("selected checklist table not uniquely identified")
    table = tables[0]
    table_id = table.get("id")
    if not table_id:
        raise ValueError("checklist table missing stable XML anchor")
    if spec.get("table_id") and table_id != spec["table_id"]:
        raise ValueError("checklist table anchor differs from pinned table")
    if table.findall(".//permissions") or table.findall(".//license"):
        raise ValueError("table has separate rights metadata requiring qualification")
    rows = []
    for position, row in enumerate(table.findall(".//tbody/tr"), start=1):
        cells = [content(cell) for cell in row if cell.tag in {"td", "th"}]
        if len(cells) < spec["id_from_right"]:
            continue
        item_id = cells[-spec["id_from_right"]].lower()
        if not ITEM_ID.fullmatch(item_id):
            continue
        phrase = cells[-spec["text_from_right"]]
        if not phrase:
            raise ValueError("numbered source row lacks requirement text")
        topic = cells[-spec["id_from_right"] - 1] if len(cells) > spec["id_from_right"] else None
        rows.append({"item_id": item_id, "topic": topic,
                     "source_anchor": f"{table_id}:row:{position}:item:{item_id}",
                     "text": phrase, "normalized_text_sha256": digest(phrase)})
    if [row["item_id"] for row in rows] != spec["item_ids"]:
        raise ValueError("numbered checklist rows differ from independently specified IDs/order")
    table_hash = digest(json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    if spec.get("table_rows_sha256") and table_hash != spec["table_rows_sha256"]:
        raise ValueError("source row digest differs from pinned table")
    try:
        structure = describe_table(table, rows)
    except ValueError:
        structure = {"status": "held_unsupported_structure", "issues": ["unsupported_table_layout"]}
    return {
        "structure": structure,
        "table_rows_sha256": table_hash,
        "source_sha256": checksum, "source_bytes": len(raw), "doi": spec["doi"],
        "pmcid": spec["pmcid"], "table_id": table_id, "table_label": spec["table_label"],
        "licence": spec["licence"], "attribution": spec["attribution"],
        "rights": "article_licence_observed_table_reuse_candidate",
        "pin_status": "matched_pinned_source" if spec.get("source_sha256") else "newly_acquired_unpinned_source",
        "rows": rows,
    }


def snapshot_table(edition: dict, spec: dict) -> dict:
    """Bind a retained attributed table projection to the observed primary source pins."""
    expected = {
        "edition": spec["edition"], "doi": spec["doi"], "pmcid": spec["pmcid"],
        "source_sha256": spec["source_sha256"], "attribution": spec["attribution"],
        "source_url": "https://www.ebi.ac.uk/europepmc/webservices/rest/" + spec["pmcid"] + "/fullTextXML",
        "licence_url": "https://" + LICENCE[spec["licence"]] + "/",
    }
    if any(edition.get(key) != value for key, value in expected.items()):
        raise ValueError("snapshot edition identity, source pin, licence or attribution mismatch")
    rows = []
    for row in edition.get("rows", []):
        if not isinstance(row, dict) or set(row) != {"item_id", "topic", "source_anchor", "text"}:
            raise ValueError("invalid retained source row")
        phrase = row["text"]
        if (not isinstance(phrase, str) or not phrase or normalize(phrase) != phrase or
            not isinstance(row["source_anchor"], str) or
            not re.fullmatch(re.escape(spec["table_id"]) + r":row:[1-9]\d*:item:" +
                             re.escape(row["item_id"]), row["source_anchor"])):
            raise ValueError("invalid retained requirement or source anchor")
        rows.append({**row, "normalized_text_sha256": digest(phrase)})
    if [row["item_id"] for row in rows] != spec["item_ids"]:
        raise ValueError("retained source item identity/order mismatch")
    table_hash = digest(json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    if table_hash != spec["table_rows_sha256"]:
        raise ValueError("retained table digest differs from primary source pin")
    return {"source_sha256": spec["source_sha256"], "source_bytes": spec["source_bytes"],
            "doi": spec["doi"], "pmcid": spec["pmcid"], "table_id": spec["table_id"],
            "table_label": spec["table_label"], "table_rows_sha256": table_hash,
            "licence": spec["licence"], "attribution": spec["attribution"],
            "rights": "article_licence_observed_table_reuse_candidate",
            "pin_status": "retained_table_snapshot_matches_pinned_rows",
            "structure": {"status": "not_retained_in_flat_snapshot", "issues": ["pinned_xml_required"]},
            "rows": rows}


def parse_legacy(markdown: str) -> list[dict]:
    """Reuse the bounded legacy structure reader; keep original IDs and anchors."""
    return [{**{key: value for key, value in row.items() if key != "raw_text"},
             "text": normalize(row["text"])} for row in parse_legacy_tasks(markdown)]


def reconcile_items(source: list[dict], legacy: list[dict], *, linguistic: bool = False, nlp=None) -> dict:
    """No automatic matching based on printed numbers or approximate text."""
    items = []
    matched = set()
    source_ids = Counter(row['item_id'] for row in source)
    for row in source:
        exact = [entry["position"] for entry in legacy if row["text"] == entry["text"]]
        matched.update(exact)
        # Only a single terminal full stop is ignored in this separate diagnostic.
        # Internal punctuation and all words remain unchanged. Never elevate it
        # to strict equality or methodological equivalence.
        punctuation = [entry["position"] for entry in legacy
                       if entry["position"] not in exact and
                       row["text"].removesuffix(".") == entry["text"].removesuffix(".")]
        same_number = [entry["position"] for entry in legacy if entry["declared_item_id"] == row["item_id"]]
        scored = sorted(
            ((round(SequenceMatcher(None, row["text"].casefold(), entry["text"].casefold(),
                                   autojunk=False).ratio(), 4), entry["position"]) for entry in legacy),
            key=lambda pair: (-pair[0], pair[1]))
        best = {"legacy_position": scored[0][1], "similarity": scored[0][0]} if scored else None
        items.append({
            "source_item_id": row["item_id"], "source_anchor": row["source_anchor"],
            "source_text_sha256": row["normalized_text_sha256"],
            "same_number_legacy_positions": same_number, "exact_legacy_positions": exact,
            "terminal_period_only_legacy_positions": punctuation,
            "closest_text_candidate_only": best,
            "status": ("exact_text_match_not_methodology" if len(exact) == 1 else
                       "ambiguous_exact_text" if exact else "not_exactly_reconciled"),
        })
        if linguistic or nlp is not None:
            aligned = [entry for entry in legacy if entry["declared_item_id"] == row["item_id"]]
            if source_ids[row["item_id"]] != 1 or len(aligned) != 1 or aligned[0].get("warnings"):
                items[-1]["linguistic"] = {"status": "held_ambiguous_or_missing_alignment",
                                           "canonical_packs_promoted": 0}
            else:
                items[-1]["linguistic"] = {
                    "legacy_position": aligned[0]["position"],
                    "legacy_line_numbers": aligned[0].get("line_numbers"),
                    **compare_linguistic(row["text"], aligned[0]["text"], nlp),
                }
    return {"source_item_count": len(source), "legacy_task_count": len(legacy),
            "legacy_task_anchors": [{**{key: value for key, value in entry.items() if key != "text"},
                                     "normalized_text_sha256": digest(entry["text"])} for entry in legacy],
            "exact_unique_items": sum(len(row["exact_legacy_positions"]) == 1 for row in items),
            "terminal_period_only_unique_items": sum(not row["exact_legacy_positions"] and
                                                     len(row["terminal_period_only_legacy_positions"]) == 1
                                                     for row in items),
            "legacy_positions_without_exact_source_match": [row["position"] for row in legacy
                                                              if row["position"] not in matched],
            "items": items, "canonical_packs_promoted": 0}


def audit(root: Path, source_dir: Path | None, specs: list[dict], *, linguistic: bool = False, nlp=None) -> dict:
    snapshots = None
    if source_dir is None:
        ledger = json.loads((root / "source/official/authoritative-article-rows.json").read_text(encoding="utf-8"))
        if ledger.get("schema_version") != 1:
            raise ValueError("unsupported retained table snapshot schema")
        snapshots = {edition["edition"]: edition for edition in ledger["editions"]}
        if len(snapshots) != len(ledger["editions"]) or set(snapshots) != {spec["edition"] for spec in specs}:
            raise ValueError("retained table edition coverage differs from manifest")
    editions = []
    for spec in specs:
        result = {key: spec[key] for key in ("edition", "doi", "pmcid", "legacy_path")}
        try:
            if snapshots is not None:
                source = snapshot_table(snapshots[spec["edition"]], spec)
            else:
                with (source_dir / (spec["pmcid"] + ".xml")).open("rb") as stream:
                    raw = stream.read(MAX_BYTES + 1)
                result["observed_source_sha256"] = hashlib.sha256(raw).hexdigest()
                source = extract_table(raw, spec)
            legacy_bytes = (root / spec["legacy_path"]).read_bytes()
            legacy = parse_legacy(legacy_bytes.decode("utf-8"))
            result["source"] = source
            result["legacy_view_sha256"] = hashlib.sha256(legacy_bytes).hexdigest()
            result["legacy"] = reconcile_items(source["rows"], legacy, linguistic=linguistic, nlp=nlp)
            result["status"] = "table_items_extracted_legacy_compared"
        except (OSError, UnicodeError, ValueError) as exc:
            result["status"] = "held"
            result["error_type"] = type(exc).__name__
            result["error"] = str(exc)[:300]
        editions.append(result)
    good = [edition for edition in editions if edition["status"] == "table_items_extracted_legacy_compared"]
    structure_statuses = {}
    for edition in good:
        status = edition["source"]["structure"]["status"]
        structure_statuses[status] = structure_statuses.get(status, 0) + 1
    return {"schema_version": 2,
            "claim_boundary": "Selected primary article table text and legacy comparison only; no pack, rights or methodological promotion.",
            "summary": {"editions_attempted": len(editions), "source_tables_reconciled": len(good),
                        "source_items_extracted": sum(len(e["source"]["rows"]) for e in good),
                        "structure_status_counts": structure_statuses,
                        "canonical_packs_promoted": 0},
            "editions": editions}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--source-dir", type=Path, help="Optional exact primary XML files; default uses checked-in table snapshots.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-all", action="store_true")
    parser.add_argument("--linguistic", action="store_true", help="Add bounded rule-based row diagnostics")
    parser.add_argument("--spacy-model", type=Path, help="Explicit trusted local English model directory (implies linguistic)")
    args = parser.parse_args()
    specs = json.loads((args.root / "source/official/authoritative-article-editions.json").read_text(encoding="utf-8"))
    nlp, reference = load_reference(args.spacy_model) if args.spacy_model else (None, None)
    report = audit(args.root, args.source_dir, specs, linguistic=args.linguistic, nlp=nlp)
    if args.linguistic or nlp is not None:
        report["linguistic_reference"] = {"method": "classical_linguistic_nlp_v2",
                                          "model": reference, "authority": "diagnostic_only"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"]))
    for edition in report["editions"]:
        print(edition["edition"], edition["status"], edition.get("error", ""))
    return int(args.require_all and report["summary"]["source_tables_reconciled"] != len(specs))


if __name__ == "__main__":
    raise SystemExit(main())
