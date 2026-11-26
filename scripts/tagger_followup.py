"""E10 retrospective task formulations and supervised synthetic-stratum controls."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import re
import time
from collections import Counter
from pathlib import Path

from . import extractive_development as e

CLAUSE_LABELS = {
    "applicability": "A complete scope phrase stating which study design, population or report "
    "must follow a requirement. Include the introductory scope preposition or exclusivity word.",
    "condition": "A complete contingent clause stating when a reporting requirement applies. "
    "Include the conditional conjunction and the predicate, not the object to be reported.",
    "exception": "A complete clause describing an exemption from the requirement. Include the "
    "exception conjunction or preposition and its governed words, not the requested action.",
}


def framed_predictor(extractor, frame):
    if frame not in {"clause", "per_type"}:
        raise ValueError("unknown formulation")

    def predict(text):
        groups = (
            [CLAUSE_LABELS] if frame == "clause" else [{k: v} for k, v in CLAUSE_LABELS.items()]
        )
        merged = {}
        for labels in groups:
            raw = extractor.extract_entities(
                text,
                labels,
                include_spans=True,
                include_confidence=True,
                threshold=0.5,
                overlap_policy="allow",
            )
            e.model_spans(text, raw)
            if not set(raw["entities"]) <= labels.keys():
                raise ValueError("unexpected label for formulation")
            merged.update(raw["entities"])
        response = {"entities": merged}
        return e.model_spans(text, response), response

    return predict


def cases_from_fixture():
    if e.file_hash(e.FIXTURE) != e.FIXTURE_SHA256:
        raise ValueError("fixture mismatch")
    return json.loads(e.FIXTURE.read_text(encoding="utf-8"))


def folds(cases):
    if len({c["id"] for c in cases}) != len(cases) or len({c["text"] for c in cases}) != len(cases):
        raise ValueError("nonunique case identity or text")
    families = sorted({c["family"] for c in cases})
    if len(families) < 2:
        raise ValueError("need at least two synthetic strata")
    return [
        (f, [c for c in cases if c["family"] != f], [c for c in cases if c["family"] == f])
        for f in families
    ]


def tokens(text):
    return [(m[0], m.start(), m.end()) for m in re.finditer(r"\w+|[^\w\s]", text)]


def bio_labels(words, case, kind):
    tags = ["O"] * len(words)
    for label, start, end in e.references(case):
        if label != kind:
            continue
        indices = [i for i, (_, a, b) in enumerate(words) if a >= start and b <= end]
        if not indices or words[indices[0]][1] != start or words[indices[-1]][2] != end:
            raise ValueError("reference is not token aligned")
        for offset, i in enumerate(indices):
            if tags[i] != "O":
                raise ValueError("same-type overlapping spans not supported")
            tags[i] = "B" if offset == 0 else "I"
    return tags


def decode_bio(words, tags, kind):
    result = []
    start = None
    end = 0
    for (_, a, b), tag in zip(words, tags, strict=True):
        if start is not None and tag != "I":
            result.append((kind, start, end))
            start = None
        if tag in {"B", "I"}:
            if start is None:
                start = a
            end = b
    if start is not None:
        result.append((kind, start, end))
    return result


class NB:
    """Small fitted categorical-feature multinomial NB; no calibrated probability claim."""

    def __init__(self):
        self.counts = Counter()
        self.features = {}
        self.vocab = set()

    def fit(self, examples):
        if not examples:
            raise ValueError("empty supervised training set")
        for feats, label in examples:
            self.counts[label] += 1
            self.features.setdefault(label, Counter()).update(feats)
            self.vocab.update(feats)
        return self

    def distribution(self, feats):
        if not self.counts:
            raise ValueError("untrained classifier")
        logp = {
            label: math.log(n / sum(self.counts.values()))
            + sum(
                math.log(
                    (self.features[label][f] + 1)
                    / (sum(self.features[label].values()) + len(self.vocab) + 1)
                )
                for f in feats
                if f in self.vocab
            )
            for label, n in self.counts.items()
        }
        maximum = max(logp.values())
        values = {k: math.exp(v - maximum) for k, v in logp.items()}
        total = sum(values.values())
        return {k: v / total for k, v in values.items()}

    def predict(self, feats):
        p = self.distribution(feats)
        return min(p, key=lambda k: (-p[k], k))


def word_at(words, i):
    return words[i][0].casefold() if 0 <= i < len(words) else "<boundary>"


def token_features(words, i):
    raw = words[i][0]
    return [
        *(f"w{j}={word_at(words, i + j)}" for j in (-2, -1, 0, 1, 2)),
        "suffix=" + raw.casefold()[-3:],
        f"initial={i == 0}",
        f"upper={raw[:1].isupper()}",
        f"punct={not raw.isalnum()}",
    ]


def span_features(words, i, j):
    return [
        "first=" + word_at(words, i),
        "last=" + word_at(words, j),
        "before=" + word_at(words, i - 1),
        "after=" + word_at(words, j + 1),
        "prefix=" + word_at(words, i) + " " + word_at(words, i + 1),
        f"length={min(j - i + 1, 6)}",
        f"initial={i == 0}",
        f"internal_comma={any(w[0] == ',' for w in words[i : j + 1])}",
    ]


def candidates(words):
    return [(i, j) for i in range(len(words)) for j in range(i, min(len(words), i + 12))]


def fit_models(train, arm):
    models = {}
    for kind in e.LABELS:
        examples = []
        for case in train:
            words = tokens(case["text"])
            if arm == "token_bio":
                tags = bio_labels(words, case, kind)
                examples.extend((token_features(words, i), tag) for i, tag in enumerate(tags))
            elif arm == "span_boundary":
                gold = set(e.references(case))
                examples.extend(
                    (
                        span_features(words, i, j),
                        "yes" if (kind, words[i][1], words[j][2]) in gold else "no",
                    )
                    for i, j in candidates(words)
                )
            else:
                raise ValueError("unknown supervised arm")
        models[kind] = NB().fit(examples)
    return models


def predict_supervised(text, models, arm):
    words = tokens(text)
    result = []
    for kind, model in models.items():
        if arm == "token_bio":
            tags = [model.predict(token_features(words, i)) for i in range(len(words))]
            result.extend(decode_bio(words, tags, kind))
        else:
            proposed = []
            for i, j in candidates(words):
                p = model.distribution(span_features(words, i, j)).get("yes", 0.0)
                if p >= 0.5:
                    proposed.append((p, words[i][1], words[j][2]))
            accepted = []
            for _, a, b in sorted(proposed, key=lambda s: (-s[0], s[1], s[2])):
                if all(b <= x or a >= y for x, y in accepted):
                    accepted.append((a, b))
            result.extend((kind, a, b) for a, b in sorted(accepted))
    return result


def supervised(cases):
    split = folds(cases)
    arms = {"rules": e.evaluate(cases, lambda text: (e.rules(text), None))}
    for arm in ("token_bio", "span_boundary"):
        start = time.perf_counter()
        predictions = {}
        for _, train, test in split:
            models = fit_models(train, arm)
            for case in test:
                predictions[case["text"]] = predict_supervised(case["text"], models, arm)
        arms[arm] = e.evaluate(cases, lambda text, predictions=predictions: (predictions[text], None))
        arms[arm]["fit_and_predict_seconds"] = time.perf_counter() - start
    return {
        "arms": arms,
        "folds": [
            {
                "held_synthetic_stratum": f,
                "train": [x["id"] for x in tr],
                "test": [x["id"] for x in te],
            }
            for f, tr, te in split
        ],
        "status": "retrospective_author_labelled_synthetic_strata",
        "scientific_qualification": False,
    }


def main():
    import resource

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=("supervised", "clause", "per_type"), required=True)
    parser.add_argument("--model-dir", type=Path)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    start = time.perf_counter()
    status = 0
    try:
        if args.arm == "supervised":
            result = supervised(cases_from_fixture())
        else:
            extractor, runtime, assets = e.load_extractor(args.model_dir)
            result = {
                "evaluation": e.evaluate(
                    cases_from_fixture(), framed_predictor(extractor, args.arm)
                ),
                "runtime": runtime,
                "assets": assets,
                "model_revision": e.MODEL_REVISION,
            }
    except (ValueError, OSError, RuntimeError, ImportError) as exc:
        result = {"status": "failed", "error": str(exc)}
        status = 1
    result.update(
        {
            "arm": args.arm,
            "revision": args.revision,
            "fixture_sha256": e.FIXTURE_SHA256,
            "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "python": platform.python_version(),
            "seconds": time.perf_counter() - start,
            "peak_process_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "scientific_qualification": False,
            "canonical_packs_promoted": 0,
            "model_weight_bytes": 0 if args.arm == "supervised" else e.MODEL_BYTES,
        }
    )
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if status:
        raise SystemExit(status)


if __name__ == "__main__":
    main()
