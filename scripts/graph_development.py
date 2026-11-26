"""E11 advisory graph retrieval on an authored synthetic fixture; not equivalence."""

import argparse
import hashlib
import json
import platform
import re
import time
from pathlib import Path

from .costing_retrieval import evaluate, lexical_rankings, rank
from .lexical_text import cosine, term_counts, tfidf_vectors

FIXTURE = Path(__file__).resolve().parents[1] / "tests/fixtures/specialist/graph-retrieval-v1.json"
FIXTURE_SHA256 = "4aa25eb689a62a7b2758e19d6821f09708563a0d0c627c91b102cd84a3ca066d"
LINK = re.compile(r"\b(See|Depends on) ([A-Z]\d+)\.")
BONUS = 0.35


def load_fixture():
    raw = FIXTURE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != FIXTURE_SHA256:
        raise ValueError("fixture hash mismatch")
    return json.loads(raw)


def index(rows):
    result = {row["id"]: row for row in rows}
    if len(result) != len(rows) or any(not row["anchor"] for row in rows):
        raise ValueError("duplicate ID or missing anchor")
    return result


def edges(data):
    headings, targets = index(data["headings"]), index(data["targets"])
    result = []
    for key, target in targets.items():
        parent = target["heading"]
        if parent not in headings:
            raise ValueError("unknown parent")
        result.append({"from": key, "to": parent, "type": "parent", "anchor": target["anchor"]})
        for match in LINK.finditer(target["text"]):
            other = match.group(2)
            if other not in targets or other == key:
                raise ValueError("invalid explicit link")
            result.append(
                {
                    "from": key,
                    "to": other,
                    "type": "crossref" if match.group(1) == "See" else "dependency",
                    "anchor": target["anchor"],
                    "span": list(match.span()),
                }
            )
    return result


def scores(queries, targets, method):
    docs = {("query", key): term_counts(text, method) for key, text in queries.items()}
    docs.update({("target", key): term_counts(text, method) for key, text in targets.items()})
    vectors = tfidf_vectors(docs)
    return {
        key: {
            target: cosine(vectors.get(("query", key), {}), vectors.get(("target", target), {}))
            for target in targets
        }
        for key in queries
    }


def compare(data):
    graph = edges(data)
    targets = {row["id"]: row["text"] for row in data["targets"]}
    headings = {row["id"]: row["text"] for row in data["headings"]}
    queries = {(row["family"], row["id"]): row["text"] for row in data["queries"]}
    refs = {(row["family"], row["id"]): set(row["relevant"]) for row in data["queries"]}
    if len(queries) != len(data["queries"]):
        raise ValueError("duplicate query")
    methods = {}
    for method in ("word", "char"):
        start = time.perf_counter()
        base = scores(queries, targets, method)
        lexical = {key: rank(row, positive=True) for key, row in base.items()}
        lexical_seconds = time.perf_counter() - start
        if lexical != lexical_rankings(queries, targets, method):
            raise ValueError("incumbent ranking mismatch")
        start = time.perf_counter()
        context = scores(queries, headings, method)
        augmented = {}
        for key, row in base.items():
            signals = {target: 0.0 for target in targets}
            for edge in graph:
                dest = edge["to"]
                if edge["type"] == "parent":
                    signal = context[key][dest]
                else:
                    signal = row[dest] * (0.8 if edge["type"] == "crossref" else 0.6)
                signals[edge["from"]] = max(signals[edge["from"]], signal)
            augmented[key] = {t: round(v + BONUS * signals[t], 6) for t, v in row.items()}
        reranked = {key: rank(row, positive=True) for key, row in augmented.items()}
        graph_seconds = time.perf_counter() - start
        baseline = evaluate(refs, set(targets), lexical)
        challenger = evaluate(refs, set(targets), reranked)
        paired = []
        for key, expected in sorted(refs.items()):
            before = expected & set(lexical[key][:5])
            after = expected & set(reranked[key][:5])
            paired.append(
                {
                    "family": key[0],
                    "query": key[1],
                    "reference": sorted(expected),
                    "lexical_hits": sorted(before),
                    "graph_hits": sorted(after),
                    "gained": sorted(after - before),
                    "lost": sorted(before - after),
                    "lexical_scores": base[key],
                    "graph_scores": augmented[key],
                }
            )
        methods[method] = {
            "baseline": baseline,
            "challenger": challenger,
            "paired": paired,
            "lexical_seconds": lexical_seconds,
            "graph_incremental_seconds": graph_seconds,
        }
    return {
        "fixture_sha256": FIXTURE_SHA256,
        "status": "synthetic_development_only",
        "equivalence_inferred": False,
        "eligible_pairs": len(targets) * len(queries),
        "reference_associations": sum(map(len, refs.values())),
        "edges": graph,
        "fixed_bonus": BONUS,
        "model_weight_bytes": 0,
        "methods": methods,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = compare(load_fixture())
    result["python"] = platform.python_version()
    result["platform"] = platform.platform()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for method, entry in result["methods"].items():
        print(
            method,
            entry["baseline"]["macro_query_recall"]["5"],
            entry["challenger"]["macro_query_recall"]["5"],
            "gained",
            sum(len(row["gained"]) for row in entry["paired"]),
            "lost",
            sum(len(row["lost"]) for row in entry["paired"]),
        )


if __name__ == "__main__":
    main()
