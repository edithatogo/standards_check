"""Real-source structural diagnostics, not independently adjudicated semantics."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import unicodedata
import zipfile
from itertools import product
from pathlib import Path

from scripts.costing_retrieval import lexical_rankings

SOURCE_SHA = "d14b546d53d43cc8a40a3c2adeecbd24923bae7d8794b599cbcefa593f879b52"
PDF_RECEIPT_SHA = "eb73a505f56986c638bca877d175562041276659ffd5a34e1db04ed937e783ae"
PACK_SHA = "56f79ee76d463c3878431a0342f127a1bcc89c019d636e4f28afdc0dfc462ec1"


def index(rows, key):
    result = {r[key]: r for r in rows}
    if len(result) != len(rows):
        raise ValueError("duplicate identity")
    return result


def topic_context(edition):
    """Compare physical and resolved topic cells against a separate literal reader."""
    expected = edition["expected_ids"]
    literal = index(edition["literal"]["rows"], "item_id")
    docx = index(edition["docx"]["anchor_evidence"], "item_id")
    groups = index(edition["literal"]["groups"], "anchor")
    if not expected or list(literal) != expected or list(docx) != expected:
        raise ValueError("row identity or order mismatch")
    cells = index([c for row in docx.values() for c in row["other_cells"]], "anchor")
    rows = []
    for key in expected:
        row, target = docx[key], groups[literal[key]["topic_anchor"]]
        if target["kind"] != "topic":
            raise ValueError("not a topic group")
        cell = cells[row["row_anchor"] + "/c1"]
        origin = cell.get("merge_origin")
        if origin and (origin not in cells or cells[origin]["text_sha256"] != cell["origin_text_sha256"]):
            raise ValueError("unbound merge origin")
        direct = cell["text_sha256"] == target["text_sha256"]
        closed = (cells[origin]["text_sha256"] if origin else cell["text_sha256"]) == target["text_sha256"]
        rows.append({"id": key, "topic_anchor": target["anchor"], "cell_anchor": cell["anchor"],
                     "merge_origin": origin, "direct": direct, "closure": closed})
    return {
        "edition": edition["edition"], "source_status": edition["status"], "n": len(rows),
        "direct": sum(r["direct"] for r in rows), "closure": sum(r["closure"] for r in rows),
        "gained": sum(r["closure"] and not r["direct"] for r in rows),
        "lost": sum(r["direct"] and not r["closure"] for r in rows), "rows": rows,
    }


def load_archive(path, expected, member):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("archive digest mismatch")
    with zipfile.ZipFile(path) as archive:
        return json.loads(archive.read(member))


def cross_reference(pack, receipt):
    """One literal reference, no semantic-relevance or independent family claim."""
    items = index(pack["requirements"], "display_number")
    rows = index(receipt["comparisons"], "item")
    if (not receipt["pack_item_source_parity"] or len(items) != 42
        or set(items) != set(rows) or receipt["pack_id"] != pack["pack_id"]
        or pack["rights"]["status"] != "cleared"):
        raise ValueError("source binding mismatch")
    for key, item in items.items():
        normalized = "".join(c for c in unicodedata.normalize("NFKC", item["verbatim_text"]) if not c.isspace())
        if (hashlib.sha256(normalized.encode()).hexdigest() != rows[key]["whitespace_normalized_text_sha256"]
            or not rows[key]["whitespace_normalized_source_match"]):
            raise ValueError("source row digest mismatch")
    # Explicit, manually inspected printed cross-reference; not derived from ranking.
    if "(item #5)" not in items["13a"]["verbatim_text"]:
        raise ValueError("explicit reference absent")
    result = []
    for method, heading, link in product(("word", "char"), (False, True), (False, True)):
        started = time.perf_counter()
        texts = {k: (v["section"] + " " if heading else "") + v["verbatim_text"] for k, v in items.items()}
        query = texts.pop("13a")
        order = lexical_rankings({"q": query}, texts, method)["q"]
        if link:
            order = ["5", *(k for k in order if k != "5")]
        rank = order.index("5") + 1 if "5" in order else None
        result.append({"method": method, "heading": heading, "link": link, "rank": rank,
                       "hit1": int(rank == 1), "hit5": int(rank is not None and rank <= 5),
                       "eligible_candidates": len(texts), "selected_at_one": order[:1],
                       "seconds": time.perf_counter() - started})
    return {"source": "13a", "target": "5", "source_anchor": items["13a"]["source_anchor"],
            "target_anchor": items["5"]["source_anchor"], "n": 1, "arms": result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--pack", type=Path, default=Path("packs/org.prisma/prisma/2020/pack.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.pack.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PACK_SHA:
        raise ValueError("pack digest mismatch")
    literal = load_archive(args.artifacts / "github-actions-artifact-15110837213.zip", SOURCE_SHA, "literal-source-comparison.json")
    pdf = load_archive(args.artifacts / "github-actions-artifact-15105308560.zip", PDF_RECEIPT_SHA, "prisma2020-source-comparison.json")
    started = time.perf_counter()
    contexts = [topic_context(e) for e in literal["editions"]]
    result = {"schema_version": 1, "boundary": "Real source structure diagnostics only; source and semantic reference holds preserved",
              "source_archive_sha256": SOURCE_SHA, "pdf_archive_sha256": PDF_RECEIPT_SHA,
              "pack_sha256": PACK_SHA, "contexts": contexts,
              "cross_reference": cross_reference(json.loads(raw), pdf),
              "context_seconds": time.perf_counter() - started, "scientific_qualification": False}
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
