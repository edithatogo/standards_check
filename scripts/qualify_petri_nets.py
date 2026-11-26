"""Bounded cross-check of maintained PNML using the locked PM4Py semantics."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from collections import deque
from pathlib import Path

from .orthogonal_checks import verify_pnml

ROOT = Path(__file__).resolve().parents[1]


def _reference(net, initial, final, max_states, max_tokens):
    from pm4py.objects.petri_net import semantics

    held = {"status": "held_limit"}
    if max(sum(initial.values()), sum(final.values())) > max_tokens:
        return held
    graph = {}
    queue = deque([initial])
    known = {initial}
    fired = set()
    proper = True
    deadlocks = 0
    while queue:
        marking = queue.popleft()
        enabled = semantics.enabled_transitions(net, marking)
        if marking == final and enabled:
            proper = False
        if marking != final and all(marking[p] >= count for p, count in final.items()):
            proper = False
        if marking != final and not enabled:
            deadlocks += 1
        graph[marking] = set()
        for transition in sorted(enabled, key=lambda t: t.name):
            successor = semantics.execute(transition, net, marking)
            if successor is None:
                raise ValueError("PM4Py enabled transition could not fire")
            if sum(successor.values()) > max_tokens:
                return held
            if successor not in known:
                if len(known) >= max_states:
                    return held
                known.add(successor)
                queue.append(successor)
            graph[marking].add(successor)
            fired.add(transition.name)
    # Independent fixed-point computation of the states with a path to completion.
    completing = {final} & known
    while True:
        previous = completing.copy()
        completing.update(m for m, targets in graph.items() if targets & previous)
        if previous == completing:
            break
    dead = sorted({t.name for t in net.transitions} - fired)
    sound = proper and completing == known and not dead
    return {
        "status": "sound_in_scope" if sound else "unsound",
        "states": len(known),
        "deadlocks": deadlocks,
        "dead_transitions": dead,
    }


def compare_net(path: Path, *, max_states: int = 1000, max_tokens: int = 100) -> dict:
    """Compare two readers and firing engines, keeping bounds and witnesses explicit."""
    import pm4py
    from pm4py.objects.petri_net import semantics

    if path.is_symlink() or path.stat().st_size > 1_000_000:
        raise ValueError("unsafe PNML input")
    raw = path.read_bytes()
    if b"<!DOCTYPE" in raw.upper():
        raise ValueError("DTD is unsupported by this comparator")
    native = verify_pnml(raw, max_states=max_states, max_tokens=max_tokens)
    net, initial, final = pm4py.read_pnml(str(path))
    reference = _reference(net, initial, final, max_states, max_tokens)
    witness = native.get("witness", [])
    witness_ok = True
    if witness or native["status"] == "sound_in_scope":
        by_name = {t.name: t for t in net.transitions}
        marking = initial
        for identifier in witness:
            if identifier not in by_name:
                witness_ok = False
                break
            marking = semantics.execute(by_name[identifier], net, marking)
            if marking is None:
                witness_ok = False
                break
        witness_ok = witness_ok and marking == final
    comparable = {key: native.get(key) for key in reference}
    return {
        **native,
        "reference": reference,
        "witness_replayed": witness_ok,
        "matched": comparable == reference and witness_ok,
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def corpus(root: Path) -> dict:
    """Qualify every maintained PNML file, with no source prose in the receipt."""
    paths = sorted((root / "petri-nets").rglob("*.pnml"))
    if not paths or len(paths) > 512:
        raise ValueError("missing or oversized maintained net inventory")
    rows = []
    for path in paths:
        result = compare_net(path)
        rows.append({"path": path.relative_to(root).as_posix(), **result})
    return {
        "protocol": "bounded-pnml-pm4py-v1",
        "pm4py_version": importlib.metadata.version("pm4py"),
        "max_states": 1000,
        "max_tokens": 100,
        "nets": rows,
        "qualified": all(row["matched"] and row["status"] != "held_limit" for row in rows),
        "boundary": "Structural marking behavior only; not reporting-methodology acceptance.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = corpus(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if result["qualified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
