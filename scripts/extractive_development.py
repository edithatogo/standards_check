"""E10 short synthetic typed-span comparison, never a source admission decision."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import re
import time
from collections import Counter
from importlib.metadata import version
from pathlib import Path

FIXTURE = Path(__file__).resolve().parents[1] / "tests/fixtures/specialist/qualifier-spans-v1.json"
FIXTURE_SHA256 = "759af7289d9cecd51c7d5b2b788a082b9cc7859e5ddca6ab54f5e40b0ecf5ac9"
MODEL_REVISION = "0f9bfda3394fe71b6e2cd479b98d08eca5ba6f0b"
MODEL_SHA256 = "4ee982787ace270d4bf15dbcb28ced38e0aa201372347114ceedd6336055de2b"
MODEL_BYTES = 295_567_700
ASSETS = (
    "model.safetensors",
    "config.json",
    "encoder_config/config.json",
    "tokenizer.json",
    "tokenizer_config.json",
)
RUNTIME = {"gliner2": "2.2.0", "transformers": "5.8.0", "torch": "2.10.0+cpu"}
LABELS = {
    "applicability": "Exact phrase specifying the study, report, setting or population to which "
    "the obligation applies, including the scope marker.",
    "condition": "Complete positive contingent clause that triggers the reporting obligation, "
    "including if, when or other conditional marker; not a date being requested.",
    "exception": "Complete clause excluding an otherwise applicable reporting obligation, "
    "including the exception marker if present.",
}
MARKER = re.compile(
    r"\b(?:only for|for|in|except when|except in|except|unless|provided that|if|when)\b", re.I
)


def rules(text):
    """Simple clause heuristic: preserve exact source characters, no inference."""
    found = []
    for match in MARKER.finditer(text):
        marker = match[0].casefold()
        if marker in {"for", "in", "only for"} and match.start() != 0:
            continue
        if marker.startswith("except") or marker == "unless":
            kind = "exception"
        elif marker in {"for", "in", "only for"}:
            kind = "applicability"
        else:
            kind = "condition"
        rest = text[match.end() :]
        end = re.search(r"[,;.:)]|\b(?:unless|except|provided that|if|when)\b", rest, re.I)
        stop = match.end() + (end.start() if end else len(rest))
        stop = match.start() + len(text[match.start() : stop].rstrip())
        if stop > match.end():
            found.append((kind, match.start(), stop))
    return found


def references(case):
    text = case["text"]
    spans = []
    for kind, phrase in case["labels"]:
        if kind not in LABELS or not phrase or text.count(phrase) != 1:
            raise ValueError("nonunique or invalid reference span")
        start = text.index(phrase)
        spans.append((kind, start, start + len(phrase)))
    if len(spans) != len(set(spans)):
        raise ValueError("duplicate reference span")
    return spans


def model_spans(text, response):
    """Reject invalid offsets/labels; never search for a guessed occurrence."""
    entities = response.get("entities") if isinstance(response, dict) else None
    if not isinstance(entities, dict) or not set(entities) <= LABELS.keys():
        raise ValueError("invalid entity result")
    spans = []
    for kind, items in entities.items():
        if not isinstance(items, list):
            raise ValueError("invalid span list")
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("invalid span")
            start, end, confidence = item.get("start"), item.get("end"), item.get("confidence")
            if (
                type(start) is not int
                or type(end) is not int
                or not 0 <= start < end <= len(text)
                or text[start:end] != item.get("text")
                or type(confidence) not in (int, float)
                or not math.isfinite(confidence)
                or not 0 <= confidence <= 1
            ):
                raise ValueError("span does not round-trip to source or confidence invalid")
            spans.append((kind, start, end))
    return spans


def evaluate(cases, predict):
    """Score all cases, including abstentions; duplicates are false positives."""
    rows = []
    totals = {kind: Counter() for kind in LABELS}
    for case in cases:
        text = case["text"]
        expected = Counter(references(case))
        raw = None
        error = None
        try:
            predicted, raw = predict(text)
        except ValueError as exc:
            predicted, error = [], str(exc)
        observed = Counter(predicted)
        missing, extra = expected - observed, observed - expected
        for kind, counter in totals.items():
            counter["tp"] += sum(n for span, n in (expected & observed).items() if span[0] == kind)
            counter["fn"] += sum(n for span, n in missing.items() if span[0] == kind)
            counter["fp"] += sum(n for span, n in extra.items() if span[0] == kind)
        rows.append(
            {
                "id": case["id"],
                "family": case["family"],
                "text": text,
                "expected": list(expected.elements()),
                "predicted": predicted,
                "missing": list(missing.elements()),
                "extra": list(extra.elements()),
                "no_spans": not predicted,
                "invalid_abstention": error,
                "raw": raw,
            }
        )
    combined = sum(totals.values(), Counter())
    scores = {}
    for kind, count in {**totals, "all": combined}.items():
        tp, fp, fn = (count[k] for k in ("tp", "fp", "fn"))
        scores[kind] = {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": tp / (tp + fp) if tp + fp else None,
            "recall": tp / (tp + fn) if tp + fn else None,
            "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None,
        }
    return {
        "scores": scores,
        "cases": rows,
        "invalid_abstentions": sum(bool(r["invalid_abstention"]) for r in rows),
        "no_span_cases": sum(r["no_spans"] for r in rows),
        "missed_qualifiers": combined["fn"],
    }


def model_predictor(extractor):
    def predict(text):
        raw = extractor.extract_entities(
            text,
            LABELS,
            include_spans=True,
            include_confidence=True,
            threshold=0.5,
            overlap_policy="allow",
        )
        return model_spans(text, raw), raw

    return predict


def file_hash(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load_extractor(directory):
    runtime = {name: version(name) for name in RUNTIME}
    if runtime != RUNTIME or directory is None:
        raise ValueError("unpinned local runtime or missing model directory")
    asset_info = {
        name: {"sha256": file_hash(directory / name), "bytes": (directory / name).stat().st_size}
        for name in ASSETS
    }
    if asset_info["model.safetensors"] != {"sha256": MODEL_SHA256, "bytes": MODEL_BYTES}:
        raise ValueError("unqualified model weights")
    import torch
    from gliner2 import AutoExtractor

    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    torch.manual_seed(0)
    extractor = AutoExtractor.from_pretrained(
        str(directory), map_location="cpu", local_files_only=True
    )
    extractor.eval()
    return extractor, runtime, asset_info


def load_model(directory):
    extractor, runtime, asset_info = load_extractor(directory)
    return model_predictor(extractor), runtime, asset_info


def run(arm, directory, revision):
    import resource

    start = time.perf_counter()
    if file_hash(FIXTURE) != FIXTURE_SHA256:
        raise ValueError("fixture bytes differ from the frozen development input")
    cases = json.loads(FIXTURE.read_text(encoding="utf-8"))
    asset_info = {}
    runtime = {}
    if arm == "rules":

        def predict(text):
            return rules(text), None

    elif arm == "gliner":
        predict, runtime, asset_info = load_model(directory)
    else:
        raise ValueError("unsupported arm")
    result = evaluate(cases, predict)
    return {
        "experiment": "E10-qualifier-spans-development-v1",
        "arm": arm,
        "revision": revision,
        "reference_status": "author_labelled_synthetic",
        "scientific_qualification": False,
        "canonical_packs_promoted": 0,
        "fixture_sha256": file_hash(FIXTURE),
        "script_sha256": file_hash(Path(__file__)),
        "runtime": runtime,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "model_revision": MODEL_REVISION if asset_info else None,
        "model_weight_bytes": MODEL_BYTES if asset_info else 0,
        "assets": asset_info,
        "seconds": time.perf_counter() - start,
        "peak_process_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        **result,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=("rules", "gliner"), required=True)
    parser.add_argument("--model-dir", type=Path)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = run(args.arm, args.model_dir, args.revision)
    except (ValueError, OSError, RuntimeError, ImportError) as exc:
        result = {
            "arm": args.arm,
            "revision": args.revision,
            "status": "failed",
            "error": str(exc),
            "scientific_qualification": False,
            "canonical_packs_promoted": 0,
        }
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        raise SystemExit(1) from exc
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
