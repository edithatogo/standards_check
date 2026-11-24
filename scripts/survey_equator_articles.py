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
from pathlib import Path
import re
import time
from urllib.parse import urlencode
from xml.etree import ElementTree as ET

if __package__:
    from .reconcile_authoritative_articles import (
        LICENCE, MAX_BYTES, ITEM_ID, content, digest, extract_table,
        parse_legacy, reconcile_items,
    )
else:
    from reconcile_authoritative_articles import (
        LICENCE, MAX_BYTES, ITEM_ID, content, digest, extract_table,
        parse_legacy, reconcile_items,
    )

HOST = "www.ebi.ac.uk"
API = "/europepmc/webservices/rest/"
DOI = re.compile(r"10\.\d{4,9}/[A-Za-z0-9._;()/:+<>\-]{1,220}", re.I)
PMID = re.compile(r"[1-9]\d{0,9}")
PMCID = re.compile(r"PMC[1-9]\d{0,9}")
BATCH_SIZE = 20


def identifiers(row: dict) -> tuple[str | None, str | None]:
    pmid, doi = row.get("pmid"), row.get("doi")
    return (pmid if isinstance(pmid, str) and PMID.fullmatch(pmid) else None,
            doi.lower() if isinstance(doi, str) and DOI.fullmatch(doi) else None)


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


def catalogue_report(catalogue: dict, records: list[dict], failed_terms: set[str]) -> dict:
    rows = catalogue["guidelines"]
    if len(rows) != catalogue["published_count"] or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("incomplete or duplicated catalogue")
    if not re.fullmatch(r"[a-f0-9]{40}", catalogue["source_revision"]):
        raise ValueError("unpinned upstream catalogue")
    out = []
    for row in rows:
        result = resolve(row, records)
        if failed_terms.intersection(query_terms([row])):
            result = {"id": row["id"], "source_blob_sha": row["source_blob_sha"],
                      "status": "lookup_incomplete"}
        out.append(result)
    return {"schema_version": 1, "source_revision": catalogue["source_revision"],
            "summary": {"published_count": len(out),
                        "status_counts": dict(sorted(Counter(r["status"] for r in out).items())),
                        "canonical_packs_promoted": 0},
            "records": out}


def get_bytes(path: str, max_bytes: int) -> bytes:
    # Fixed official host, HTTPS, no redirects or arbitrary publisher URL requests.
    conn = http.client.HTTPSConnection(HOST, timeout=20)
    try:
        conn.request("GET", path, headers={"Accept": "*/*",
                     "User-Agent": "StandardFlow-source-evidence/1.0"})
        response = conn.getresponse()
        if response.status != 200:
            raise OSError(f"Europe PMC HTTP {response.status}")
        raw = response.read(max_bytes + 1)
        if len(raw) > max_bytes:
            raise ValueError("provider response too large")
        return raw
    finally:
        conn.close()


def lookup(rows: list[dict]) -> tuple[list[dict], set[str]]:
    terms = query_terms(rows)
    records, failed = [], set()
    for start in range(0, len(terms), BATCH_SIZE):
        batch = terms[start:start+BATCH_SIZE]
        query = urlencode({"query": " OR ".join(batch), "format": "json",
                           "resultType": "core", "pageSize": 100, "synonym": "false"})
        try:
            response = json.loads(get_bytes(API + "search?" + query, 12_000_000))
            hits = response["resultList"]["result"]
            if response["hitCount"] != len(hits):
                # Never treat a truncated result page as an authoritative absence.
                raise ValueError("incomplete provider result")
            records.extend(hits)
        except (OSError, ValueError, KeyError, TypeError, http.client.HTTPException):
            failed.update(batch)
        time.sleep(0.35)
    return records, failed


def scan_article(raw: bytes, spec: dict, root: Path | None) -> dict:
    if not raw or len(raw) > MAX_BYTES or re.search(rb"<!ENTITY", raw, re.I):
        raise ValueError("empty, oversized or entity-bearing article")
    try:
        article = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError("invalid article XML") from exc
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
        try:
            if not PMCID.fullmatch(spec["pmcid"]):
                raise ValueError("invalid selected PMCID")
            raw = get_bytes(API + spec["pmcid"] + "/fullTextXML", MAX_BYTES)
            results.append(scan_article(raw, spec, root))
        except (OSError, ValueError, http.client.HTTPException) as exc:
            results.append({"edition": spec["edition"], "doi": spec["doi"], "pmcid": spec["pmcid"],
                            "status": "held", "error_type": type(exc).__name__,
                            "reason": str(exc)[:150], "canonical_packs_promoted": 0})
        time.sleep(0.35)
    return results


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalogue", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    catalogue = json.loads(args.catalogue.read_text(encoding="utf-8"))
    records, failed = lookup(catalogue["guidelines"])
    report = catalogue_report(catalogue, records, failed)
    specs = json.loads((root/"source/official/priority-article-candidates.json").read_text(encoding="utf-8"))
    report["priority_articles"] = priority_survey(specs, root)
    report["summary"]["priority_status_counts"] = dict(sorted(Counter(r["status"] for r in report["priority_articles"]).items()))
    report["summary"]["metadata_batches_failed_terms"] = len(failed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report["summary"], sort_keys=True))
    for record in report["priority_articles"]:
        print(record["edition"], record["status"], record.get("matched_rows",0), "/", record.get("expected_rows",0))


if __name__ == "__main__":
    main()
