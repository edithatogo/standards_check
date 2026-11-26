"""Advisory catalogue topic projection; never an ontology equivalence or rights decision."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import zipfile
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ARCHIVE_SHA = "21046589502f064d54800c9f495d72d18b97184a1db376f06da773b84bde3f01"
PACK_SHA = "56f79ee76d463c3878431a0342f127a1bcc89c019d636e4f28afdc0dfc462ec1"
FACETS = ("study_types", "clinical_areas", "report_sections")
UNKNOWN_DESIGN = "No study design specified"


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def mentions(text, terms):
    """Longest nonoverlapping literal spans; offsets refer to the original text."""
    found = []
    for term in terms:
        for alias in term["aliases"]:
            for match in re.finditer(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", text, re.I):
                # Do not turn a hyphenated non-randomized mention into randomization.
                if re.search(r"\bnon[-\s]$", text[: match.start()], re.I):
                    continue
                found.append((match.start(), match.end(), term["id"]))
    selected = []
    for start, end, concept in sorted(set(found), key=lambda x: (x[0], -(x[1]-x[0]), x[2])):
        if not any(start < r["end"] and end > r["start"] for r in selected):
            selected.append({"concept": concept, "start": start, "end": end,
                             "span_sha256": digest(text[start:end])})
    return selected


def hierarchy(terms):
    """MeSH tree placement ancestry, not an OWL subsumption/equivalence assertion."""
    edges = []
    for child in terms:
        for parent in terms:
            if child["id"] == parent["id"]:
                continue
            paths = sorted([a, b] for a in child["trees"] for b in parent["trees"]
                           if a.startswith(b + "."))
            if paths:
                edges.append({"source": child["id"], "target": parent["id"],
                              "predicate": "mesh_tree_ancestor", "tree_pairs": paths})
    return edges


def project(catalogue, terms, pack=None):
    rows = catalogue["guidelines"]
    revision = catalogue["source_revision"]
    ids = {r["id"] for r in rows}
    if (not rows or len(rows) != len(ids) or len(ids) != catalogue["published_count"]
        or not re.fullmatch(r"[0-9a-f]{40}", revision)
        or any(not r["id"].startswith("equator:") or not re.fullmatch(r"[0-9a-f]{40}", r["source_blob_sha"]) for r in rows)):
        raise ValueError("catalogue identity or count mismatch")
    concepts = {t["id"]: t for t in terms}
    if not concepts or len(concepts) != len(terms) or any(
        not re.fullmatch(r"D[0-9]{6,9}", t["id"]) or not t["trees"] or not t["aliases"]
        for t in terms
    ):
        raise ValueError("invalid or duplicate concept inventory")
    aliases = defaultdict(set)
    for t in terms:
        for alias in t["aliases"]:
            aliases[alias.casefold()].add(t["id"])
    if any(len(ids) > 1 for ids in aliases.values()):
        raise ValueError("ambiguous lexical concept mapping")
    edges = hierarchy(terms)
    ancestors = defaultdict(set)
    for edge in edges:
        ancestors[edge["source"]].add(edge["target"])
    nodes = [{"id": t["id"], "kind": "mesh_descriptor", "label": t["label"], "iri": "http://id.nlm.nih.gov/mesh/" + t["id"], "trees": t["trees"]}
             for t in terms]
    facets = {f: Counter() for f in FACETS}
    facet_nodes = {}
    direct, expanded, requirements = defaultdict(set), defaultdict(set), defaultdict(set)
    cooccurrence = Counter()
    counts = Counter()
    by_category = Counter()
    for row in sorted(rows, key=lambda r: r["id"]):
        key = row["id"]
        title = row.get("title")
        nodes.append({"id": key, "kind": "catalogue_entry", "source_blob_sha": row["source_blob_sha"],
                      "metadata_status": row["metadata_status"], "title_sha256": digest(title) if title else None})
        for facet in FACETS:
            values = row.get(facet)
            counts[facet + "_null"] += int(values is None)
            values = [] if values is None else values
            if not isinstance(values, list) or any(not isinstance(v, str) or not v for v in values) or len(values) != len(set(values)):
                raise ValueError("invalid facet values")
            facets[facet].update(values)
            counts[facet + "_missing"] += int(not values)
            for value in sorted(values):
                target = "facet:" + facet + ":" + digest(value)
                facet_nodes[target] = (facet, value)
                edges.append({"source": key, "target": target, "predicate": "equator_declared_category"})
        counts["title_missing"] += int(not title)
        matches = mentions(title, terms) if title else []
        preferred = mentions(title, [{**t, "aliases": [t["label"]]} for t in terms]) if title else []
        counts["title_preferred_label_matched"] += bool(preferred)
        topics = {m["concept"] for m in matches}
        expanded_topics = topics | {parent for t in topics for parent in ancestors[t]}
        counts["title_matched"] += bool(topics)
        counts["title_matched_multiple_topics"] += len(topics) > 1
        for match in matches:
            edges.append({"source": key, "target": match["concept"], "predicate": "title_mention_candidate", "role": "unresolved_scope_or_context", **match})
        for concept in topics:
            direct[concept].add(key)
        for concept in expanded_topics:
            expanded[concept].add(key)
        for pair in combinations(sorted(topics), 2):
            cooccurrence[pair] += 1
        categories = {concepts[t].get("category") for t in expanded_topics} - {None}
        declared = set(row.get("study_types") or [])
        novel = categories - declared
        counts["entries_with_design_candidate"] += bool(categories)
        counts["unspecified_design_with_candidate"] += bool(categories and UNKNOWN_DESIGN in declared)
        counts["unverified_category_candidates"] += len(novel)
        counts["entries_with_unverified_category_candidate"] += bool(novel)
        counts["candidate_category_pairs"] += len(categories)
        counts["candidate_category_pairs_already_declared"] += len(categories & declared)
        for category in sorted(novel):
            by_category[category] += 1
            target = "facet:study_types:" + digest(category)
            facet_nodes[target] = ("study_types", category)
            edges.append({"source": key, "target": target, "predicate": "study_type_review_candidate",
                          "supporting_concepts": sorted(t for t in expanded_topics if concepts[t].get("category") == category)})
    for term in terms:
        category = term.get("category")
        if category is not None:
            target = "facet:study_types:" + digest(category)
            facet_nodes[target] = ("study_types", category)
            edges.append({"source": term["id"], "target": target,
                          "predicate": "local_study_type_hint"})
    nodes.extend({"id": k, "kind": "facet_value", "facet": facet, "label": value,
                  "declared_count": facets[facet][value]}
                 for k, (facet, value) in sorted(facet_nodes.items()))
    if pack is not None:
        if pack["rights"]["status"] != "cleared" or pack["verification"]["status"] != "source_reconciled":
            raise ValueError("pack rights or source qualification held")
        items = pack["requirements"]
        if len({r["id"] for r in items}) != len(items) or not items:
            raise ValueError("requirement identity mismatch")
        for row in items:
            if not row["rights"].get("inherit_from_pack") or not row["source_anchor"]:
                raise ValueError("item rights or source anchor held")
            key = row["id"]
            text = row["verbatim_text"]
            nodes.append({"id": key, "kind": "requirement", "pack_id": pack["pack_id"],
                          "pack_version": pack["version"], "source_anchor": row["source_anchor"],
                          "text_sha256": digest(text)})
            matches = mentions(text, terms)
            counts["requirement_matched"] += bool(matches)
            for match in matches:
                requirements[match["concept"]].add(key)
                edges.append({"source": key, "target": match["concept"], "predicate": "requirement_mention_candidate",
                              "role": "unresolved_obligation_or_context", "source_anchor": row["source_anchor"], **match})
        counts["requirement_items"] = len(items)
    node_ids = {n["id"] for n in nodes}
    if len(node_ids) != len(nodes) or any(e["source"] not in node_ids or e["target"] not in node_ids for e in edges):
        raise ValueError("unbound graph identity")
    topic_counts = {key: {"label": concepts[key]["label"], "title_direct": len(direct[key]),
                          "title_with_ancestors": len(expanded[key]), "requirement_direct": len(requirements[key])}
                    for key in sorted(concepts)}
    summary = {"directory_entries": len(rows), **dict(counts), "facets": {f: dict(c) for f, c in facets.items()},
               "topic_counts": topic_counts, "title_mentions": sum(e["predicate"] == "title_mention_candidate" for e in edges),
               "requirement_mentions": sum(e["predicate"] == "requirement_mention_candidate" for e in edges),
               "title_graph_ancestor_additions": sum(len(expanded[k] - direct[k]) for k in concepts),
               "study_type_review_candidates": dict(by_category), "nodes": len(nodes),
               "edges_by_type": dict(Counter(e["predicate"] for e in edges)), "canonical_packs_promoted": 0}
    return {"schema_version": 1, "source_revision": revision, "mesh_descriptor_observation_year": 2026,
            "boundary": "Internal exploratory topic mentions; no applicability, equivalence, independent accuracy, rights or release claim",
            "summary": summary, "nodes": nodes, "edges": edges,
            "topic_cooccurrence": [{"source": a, "target": b, "entries": n} for (a,b),n in sorted(cooccurrence.items())]}


def read_pinned(path, expected):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("input digest mismatch")
    return raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalogue-artifact", type=Path, required=True)
    parser.add_argument("--terms", type=Path, default=Path(__file__).with_name("mesh-selected-v1.json"))
    parser.add_argument("--pack", type=Path, default=Path("packs/org.prisma/prisma/2020/pack.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    read_pinned(args.catalogue_artifact, ARCHIVE_SHA)
    with zipfile.ZipFile(args.catalogue_artifact) as archive:
        catalogue = json.loads(archive.read("equator-catalogue.json"))
    pack = json.loads(read_pinned(args.pack, PACK_SHA))
    raw_terms = args.terms.read_bytes()
    terms = json.loads(raw_terms)["terms"]
    start = time.perf_counter()
    report = project(catalogue, terms, pack)
    report.update(input_archive_sha256=ARCHIVE_SHA, pack_sha256=PACK_SHA,
                  term_projection_sha256=hashlib.sha256(raw_terms).hexdigest(),
                  implementation_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    report["snapshot_sha256"] = hashlib.sha256(
        json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()
    report["projection_seconds"] = time.perf_counter()-start
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
