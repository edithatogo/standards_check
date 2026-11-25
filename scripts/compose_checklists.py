"""Local composition preview and sparse cross-pack similarity candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

from .lexical_text import normalise
from .validate_packs import validator

MAX_REQUIREMENTS = 1000
MAX_TEXT_CHARS = 8192
MAX_PACK_BYTES = 4_000_000


def compose(packs: list[dict], *, top_k: int = 5) -> dict:
    """Preserve every obligation; only repeat selection of identical packs is deduplicated."""
    if type(top_k) is not int or not 1 <= top_k <= 20:
        raise ValueError("top_k must be an integer in 1..20")
    if not packs:
        raise ValueError("select at least one reporting checklist")
    schema = validator("standard-pack.v1.schema.json")
    selected = {}
    for pack in packs:
        schema.validate(pack)
        if pack["kind"] not in {"reporting", "protocol"}:
            raise ValueError("select only reporting or protocol packs")
        identity = pack["pack_id"]
        digest = hashlib.sha256(json.dumps(pack, sort_keys=True).encode()).hexdigest()
        if identity in selected and selected[identity][1] != digest:
            raise ValueError("conflicting pack identity; select exactly one version")
        selected[identity] = (pack, digest)

    pack_rows, nodes, documents = [], [], {}
    for identity, (pack, digest) in sorted(selected.items()):
        pack_rows.append(
            {
                "pack_id": identity,
                "version": pack["version"],
                "kind": pack["kind"],
                "pack_content_sha256": digest,
                "source_sha256": pack["authority"]["source_sha256"],
            }
        )
        ids = set()
        for ordinal, item in enumerate(pack["requirements"], 1):
            if len(nodes) >= MAX_REQUIREMENTS:
                raise ValueError("selected requirement limit exceeded")
            if item["id"] in ids:
                raise ValueError("duplicate requirement identity")
            ids.add(item["id"])
            key = (identity, pack["version"], item["id"])
            rights = item["rights"]
            effective = pack["rights"] if rights.get("inherit_from_pack") else rights
            if pack["rights"]["status"] != "cleared" or effective["status"] != "cleared":
                status = "held_rights"
            elif pack["verification"]["status"] == "imported_unverified":
                status = "held_source"
            else:
                text = item["normalized_requirement"]
                if len(text) > MAX_TEXT_CHARS:
                    raise ValueError("normalized text limit exceeded")
                words = normalise(text).split()
                status = "held_no_terms"
                if words:
                    terms = Counter(words)
                    terms.update(" ".join(pair) for pair in zip(words, words[1:], strict=False))
                    documents[key] = terms
                    status = "candidate_review"
            nodes.append(
                {
                    "key": list(key),
                    "ordinal": ordinal,
                    "source_anchor": item["source_anchor"],
                    "status": status,
                }
            )

    frequencies = Counter(term for terms in documents.values() for term in terms)
    vectors = {}
    for key, terms in documents.items():
        weights = {
            term: count * (1 + math.log((1 + len(documents)) / (1 + frequencies[term])))
            for term, count in terms.items()
        }
        norm = math.sqrt(math.fsum(value * value for value in weights.values()))
        vectors[key] = {term: weight / norm for term, weight in weights.items()}
    edges = []
    # ponytail: exhaustive sparse comparison for <=1000 selected items; profile before indexing.
    for query, left in sorted(vectors.items()):
        ranked = []
        for candidate, right in vectors.items():
            if candidate[0] == query[0]:
                continue
            score = round(min(1.0, math.fsum(v * right.get(t, 0) for t, v in left.items())), 6)
            if score > 0:
                ranked.append((-score, candidate))
        for negative_score, candidate in sorted(ranked)[:top_k]:
            edges.append(
                {
                    "query": list(query),
                    "candidate": list(candidate),
                    "score": -negative_score,
                    "status": "candidate_similarity",
                }
            )
    return {
        "method": "word-unigram-bigram-tfidf-cosine-v1",
        "top_k": top_k,
        "packs": pack_rows,
        "requirements": nodes,
        "candidates": edges,
        "semantic_merges": 0,
        "applicability": "not_assessed",
        "claim_boundary": "Local candidate preview only; no equivalent relation or reporting decision.",
    }


def unique_fields(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", action="append", type=Path, required=True)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()
    packs, hashes = [], set()
    for path in args.pack:
        with path.open("rb") as handle:
            raw = handle.read(MAX_PACK_BYTES + 1)
        if len(raw) > MAX_PACK_BYTES:
            raise ValueError("pack byte limit exceeded")
        packs.append(json.loads(raw, object_pairs_hook=unique_fields))
        hashes.add(hashlib.sha256(raw).hexdigest())
    report = compose(packs, top_k=args.top_k)
    report["input_file_sha256s"] = sorted(hashes)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
