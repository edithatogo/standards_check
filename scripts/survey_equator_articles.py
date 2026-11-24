#!/usr/bin/env python3
"""Batch-resolve EQUATOR publications and survey selected authoritative OA source tables.

Outputs evidence and acquisition candidates, never canonical checklist admission.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import time
from urllib.parse import urlencode

if __package__:
    from .source_xml import parse_xml
    from .reconcile_authoritative_articles import (
        LICENCE, MAX_BYTES, ITEM_ID, content, digest, extract_table,
        parse_legacy, reconcile_items,
    )
else:
    from source_xml import parse_xml
    from reconcile_authoritative_articles import (
        LICENCE, MAX_BYTES, ITEM_ID, content, digest, extract_table,
        parse_legacy, reconcile_items,
    )

if __package__:
    from .source_provider_evidence import (EUROPE, PMCID, doi_value, pmid_value,
                                           fetch, fetch_priority, provider_observations)
else:
    from source_provider_evidence import (EUROPE, PMCID, doi_value, pmid_value,
                                         fetch, fetch_priority, provider_observations)

API = "/europepmc/webservices/rest/"
BATCH_SIZE = 20


def identifiers(row: dict) -> tuple[str | None, str | None]:
    return pmid_value(row.get("pmid")), doi_value(row.get("doi"))


def query_terms(rows: list[dict]) -> list[str]:
    pmids, dois = set(), set()
    for row in rows:
        pmid, doi = identifiers(row)
        if pmid:
            pmids.add(pmid)
        if doi:
            dois.add(doi)
    return [f"(EXT_ID:{pmid} AND SRC:MED)" for pmid in sorted(pmids)] + [
        f'DOI:"{doi}"' for doi in sorted(dois)]


def record_identity(record: dict) -> tuple:
    pmid = record.get("pmid") or (record.get("id") if record.get("source") == "MED" else None)
    doi = record.get("doi")
    return pmid, doi.lower() if isinstance(doi, str) else None, record.get("pmcid")


def resolve(row: dict, records: list[dict]) -> dict:
    pmid, doi = identifiers(row)
    result = {"id": row["id"], "source_blob_sha": row["source_blob_sha"],
              "pmid": pmid, "doi": doi}
    if not pmid and not doi:
        return {**result, "status": "missing_identifier"}
    matches = {}
    for record in records:
        rid, rdoi, pmcid = record_identity(record)
        if (pmid and rid == pmid) or (doi and rdoi == doi):
            matches[(rid, rdoi, pmcid)] = record
    if not matches:
        return {**result, "status": "unresolved_identifier"}
    exact = [record for (rid, rdoi, _), record in matches.items()
             if (not pmid or rid == pmid) and (not doi or rdoi == doi)]
    if not exact:
        return {**result, "status": "identifier_conflict"}
    if len(exact) != 1:
        return {**result, "status": "ambiguous_identifier"}
    record = exact[0]
    rid, rdoi, pmcid = record_identity(record)
    oa = record.get("isOpenAccess") == "Y"
    valid_pmcid = isinstance(pmcid, str) and PMCID.fullmatch(pmcid)
    return {**result, "status": "oa_xml_candidate" if oa and valid_pmcid else "metadata_only",
            "resolved_pmid": rid, "resolved_doi": rdoi, "pmcid": pmcid,
            "oa_reported": oa, "licence_reported": record.get("license"),
            "rights": "unassessed_article_and_table_reuse"}


def catalogue_report(catalogue: dict, records: list[dict], failed_terms: set[str],
                     deferred_terms: set[str] | None = None, retained: dict | None = None) -> dict:
    rows = catalogue["guidelines"]
    if len(rows) != catalogue["published_count"] or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("incomplete or duplicated catalogue")
    if not re.fullmatch(r"[a-f0-9]{40}", catalogue["source_revision"]):
        raise ValueError("unpinned upstream catalogue")
    out = []
    for row in rows:
        if retained and row["id"] in retained:
            out.append({**retained[row["id"]], "lookup_origin": "retained_previous_receipt"})
            continue
        result = resolve(row, records)
        terms = set(query_terms([row]))
        if failed_terms.intersection(terms) or (deferred_terms or set()).intersection(terms):
            pmid, doi = identifiers(row)
            result = {"id": row["id"], "source_blob_sha": row["source_blob_sha"],
                      "pmid": pmid, "doi": doi, "status": "lookup_incomplete",
                      "lookup_reason": "provider_request_failed" if failed_terms.intersection(terms)
                                       else "deferred_provider_circuit_breaker"}
        out.append(result)
    return {"schema_version": 1, "source_revision": catalogue["source_revision"],
            "summary": {"published_count": len(out),
                        "status_counts": dict(sorted(Counter(r["status"] for r in out).items())),
                        "canonical_packs_promoted": 0},
            "records": out}


def retained_metadata(catalogue: dict, previous: dict | None) -> dict:
    """Resume only unchanged successful identities, explicitly labelled as historical."""
    if previous is None:
        return {}
    records = previous.get("records", [])
    prior = {row["id"]: row for row in records}
    if len(prior) != len(records):
        raise ValueError("duplicate prior source identity")
    retained = {}
    for row in catalogue["guidelines"]:
        old = prior.get(row["id"], {})
        if (old.get("status") in {"oa_xml_candidate", "metadata_only"} and
            old.get("source_blob_sha") == row["source_blob_sha"] and
            (old.get("pmid"), old.get("doi")) == identifiers(row)):
            retained[row["id"]] = old
    return retained


def lookup(rows: list[dict]) -> tuple[list[dict], set[str], set[str]]:
    terms = query_terms(rows)
    records, failed, deferred = [], set(), set()
    consecutive_failures = 0
    for start in range(0, len(terms), BATCH_SIZE):
        batch = terms[start:start+BATCH_SIZE]
        if consecutive_failures >= 3:
            deferred.update(terms[start:])
            break
        query = urlencode({"query": " OR ".join(batch), "format": "json",
                           "resultType": "core", "pageSize": 100, "synonym": "false"})
        try:
            response = json.loads(fetch(EUROPE, API + "search?" + query, 12_000_000))
            hits = response["resultList"]["result"]
            if response["hitCount"] != len(hits):
                raise ValueError("incomplete provider result")
            records.extend(hits)
            consecutive_failures = 0
        except (OSError, ValueError, KeyError, TypeError, http.client.HTTPException):
            failed.update(batch)
            consecutive_failures += 1
        time.sleep(0.35)
    return records, failed, deferred


def scan_article(raw: bytes, spec: dict, root: Path | None) -> dict:
    article = parse_xml(raw, MAX_BYTES)
    meta = article.find("./front/article-meta")
    if article.tag != "article" or meta is None:
        raise ValueError("missing primary article metadata")
    ids = {e.get("pub-id-type"): content(e) for e in meta.findall("article-id")}
    if ids.get("doi", "").lower() != spec["doi"].lower():
        raise ValueError("selected DOI does not match source")
    for kind, key in (("pmid", "pmid"), ("pmc", "pmcid"), ("pmcid", "pmcid")):
        if ids.get(kind) and ids[kind].upper().removeprefix("PMC") != spec[key].removeprefix("PMC"):
            raise ValueError("article identity mismatch")
    evidence = " ".join(content(n) + " " + " ".join(v for e in n.iter() for v in e.attrib.values())
                        for n in meta.findall("./permissions/license")).lower()
    licences = [name for name, uri in LICENCE.items()
                if re.search(r"https?://" + re.escape(uri) + r"(?:/|(?=[\s.,;]|$))", evidence)]
    if len(licences) != 1:
        raise ValueError("article licence not uniquely eligible for source survey")
    result = {"edition": spec["edition"], "pmcid": spec["pmcid"], "doi": spec["doi"],
              "source_sha256": hashlib.sha256(raw).hexdigest(), "source_bytes": len(raw),
              "article_licence_observed": licences[0], "expected_rows": sum(map(len,spec["table_item_ids"])),
              "matched_rows": 0, "tables": [], "table_inventory": [],
              "rights": "table_and_item_reuse_unassessed", "canonical_packs_promoted": 0}
    wrappers = article.findall("./body//table-wrap")
    for wrapper in wrappers:
        result["table_inventory"].append({"table_id": wrapper.get("id"),
                                          "label": content(wrapper.find("label")),
                                          "caption_sha256": digest(content(wrapper.find("caption"))),
                                          "body_rows": len(wrapper.findall(".//tbody/tr"))})
    for expected in spec["table_item_ids"]:
        candidates = []
        for wrapper in wrappers:
            if not wrapper.get("id"):
                continue
            # Infer only a unique column binding with an independently specified
            # exact ordered item-ID sequence. Keep all nonmatching tables held.
            cells = [[content(c) for c in row if c.tag in {"td","th"}]
                     for row in wrapper.findall(".//tbody/tr")]
            for id_offset in (2,3,4):
                sequence = [row[-id_offset].lower() for row in cells if len(row)>=id_offset
                            and ITEM_ID.fullmatch(row[-id_offset])]
                if sequence == expected:
                    candidates.append((wrapper,id_offset))
        if len(candidates) != 1:
            continue
        wrapper, id_offset = candidates[0]
        caption = content(wrapper.find("caption"))
        label = content(wrapper.find("label")).rstrip(".")
        if not caption or not label:
            continue
        try:
            extracted = extract_table(raw, {**spec, "licence": licences[0],
                "table_id": wrapper.get("id"), "table_label": label,
                "caption_contains": caption, "id_from_right": id_offset,
                "text_from_right": id_offset-1, "item_ids": expected,
                "attribution": "Primary article DOI: " + spec["doi"]})
        except ValueError:
            continue
        rows = extracted["rows"]
        table = {"table_id": extracted["table_id"], "table_rows_sha256": extracted["table_rows_sha256"],
                 "item_ids": expected, "structure": extracted["structure"],
                 "items": [{"item_id": row["item_id"], "source_anchor": row["source_anchor"],
                            "normalized_text_sha256": row["normalized_text_sha256"]} for row in rows]}
        if root is not None and spec.get("legacy_path"):
            path = root / spec["legacy_path"]
            if path.is_file():
                table["legacy"] = reconcile_items(rows, parse_legacy(path.read_text(encoding="utf-8")))
        result["matched_rows"] += len(rows)
        result["tables"].append(table)
    result["status"] = ("expected_numbered_rows_observed"
        if result["expected_rows"] and result["expected_rows"] == result["matched_rows"]
        else "held_table_identity_or_structure")
    return result


def priority_survey(specs: list[dict], root: Path) -> list[dict]:
    results = []
    for spec in specs:
        acquisition = {}
        try:
            raw, acquisition = fetch_priority(spec["pmcid"])
            if raw is None:
                raise ValueError("both official acquisition routes unavailable or held")
            result = scan_article(raw, spec, root)
            result["acquisition"] = acquisition
            results.append(result)
        except (OSError, ValueError, http.client.HTTPException) as exc:
            results.append({"edition": spec["edition"], "doi": spec["doi"], "pmcid": spec["pmcid"],
                            "status": "held", "error_type": type(exc).__name__,
                            "reason": str(exc)[:150], "acquisition": acquisition,
                            "canonical_packs_promoted": 0})
        time.sleep(0.35)
    return results


def identifier_disagreements(row: dict, observations: dict) -> list[str]:
    """Conflicting nonempty fields are holds, not a majority-vote identity."""
    disagreements = []
    if any(v.get("status") in {"identifier_conflict", "ambiguous_identifier"} for v in observations.values()):
        disagreements.append("provider_identity_conflict")
    for field, normalize in (("pmid", pmid_value), ("doi", doi_value), ("pmcid", lambda x: x)):
        values = {normalize(v.get(field) or v.get("resolved_" + field))
                  for v in [row, *observations.values()]}
        if len(values - {None}) > 1:
            disagreements.append(field + "_disagreement")
    return disagreements


def oa_worklist(report: dict, observations: dict, priorities: list[dict], known: list[dict]) -> list[dict]:
    """Deduplicate eligible OA sources; leave actual bulk content acquisition separate."""
    known_ids = {r["pmcid"] for r in [*priorities, *known]}
    work = {}
    for row in report["records"]:
        if row.get("status") != "oa_xml_candidate":
            continue
        pmcid = row.get("pmcid")
        if not isinstance(pmcid, str) or not PMCID.fullmatch(pmcid):
            continue
        entry = work.setdefault(pmcid, {"pmcid": pmcid, "source_ids": [], "identity_pairs": [],
                                        "issues": [], "status": "candidate_pending_acquisition"})
        entry["source_ids"].append(row["id"])
        pair = [row.get("resolved_doi"), row.get("resolved_pmid")]
        if pair not in entry["identity_pairs"]:
            entry["identity_pairs"].append(pair)
        entry["issues"].extend(identifier_disagreements(row, observations.get(row["id"], {})))
        if not all(pair):
            entry["issues"].append("missing_exact_article_identifier")
    for entry in work.values():
        if len(entry["identity_pairs"]) != 1:
            entry["issues"].append("conflicting_catalogue_article_identities")
        entry["issues"] = sorted(set(entry["issues"]))
        if entry["issues"]:
            entry["status"] = "held_identity"
        elif entry["pmcid"] in known_ids:
            entry["status"] = "priority_or_retained_source"
    return [work[key] for key in sorted(work)]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalogue", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--previous", type=Path, help="Explicit prior survey receipt; reuse unchanged resolved metadata only.")
    parser.add_argument("--registry-limit", type=int, default=12, choices=range(0, 101),
                        help="Bound exact Crossref and OpenAlex singleton lookups per provider.")
    args = parser.parse_args()
    catalogue = json.loads(args.catalogue.read_text(encoding="utf-8"))
    previous_bytes = args.previous.read_bytes() if args.previous else None
    retained = retained_metadata(catalogue, json.loads(previous_bytes) if previous_bytes else None)
    specs = json.loads((root/"source/official/priority-article-candidates.json").read_text(encoding="utf-8"))
    known = json.loads((root/"source/official/authoritative-article-editions.json").read_text(encoding="utf-8"))
    # Try priority articles before exhausting the metadata provider request budget.
    priority = priority_survey(specs, root)
    records, failed, deferred = lookup([row for row in catalogue["guidelines"] if row["id"] not in retained])
    report = catalogue_report(catalogue, records, failed, deferred, retained)
    report["priority_articles"] = priority
    report["provider_evidence"] = provider_observations(
        report["records"], specs + known, os.environ.get("SOURCE_API_EMAIL"), args.registry_limit)
    evidence = report["provider_evidence"]["records"]
    for row in report["records"]:
        row["provider_disagreements"] = identifier_disagreements(row, evidence.get(row["id"], {}))
    report["oa_source_worklist"] = oa_worklist(report, evidence, specs, known)
    report["summary"]["oa_worklist_status_counts"] = dict(sorted(Counter(r["status"] for r in report["oa_source_worklist"]).items()))
    report["summary"]["priority_status_counts"] = dict(sorted(Counter(r["status"] for r in priority).items()))
    report["summary"]["metadata_batches_failed_terms"] = len(failed)
    report["summary"]["metadata_deferred_terms"] = len(deferred)
    report["summary"]["retained_metadata_records"] = len(retained)
    report["previous_receipt_sha256"] = hashlib.sha256(previous_bytes).hexdigest() if previous_bytes else None
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report["summary"], sort_keys=True))
    for record in report["priority_articles"]:
        print(record["edition"], record["status"], record.get("matched_rows",0), "/", record.get("expected_rows",0))


if __name__ == "__main__":
    main()
