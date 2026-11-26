"""Bounded HiGHS comparison for explicitly typed equivalence candidates only."""

from __future__ import annotations

from itertools import combinations


def solve(edges: list, incompatible: list) -> dict:
    """Maximize candidate weights under equivalence transitivity and hard incompatibility.

    No inferred equivalence from topic similarity, and no forced matches. Only
    candidate-edge selections are compared for uniqueness; latent pairs are not output.
    """
    import numpy as np
    from scipy.optimize import Bounds, LinearConstraint, milp

    if any(a == b or type(w) is not int or not 1 <= w <= 1_000_000 for a, b, w in edges):
        raise ValueError("invalid candidate edge")
    if any(a == b for a, b in incompatible):
        raise ValueError("self incompatibility")
    weights = {(min(a, b), max(a, b)): w for a, b, w in edges}
    if len(weights) != len(edges):
        raise ValueError("duplicate candidate edge")
    forbidden = {(min(a, b), max(a, b)) for a, b in incompatible}
    nodes = sorted({node for pair in set(weights) | forbidden for node in pair})
    if len(nodes) > 20 or len(edges) > 128:
        return {"status": "held_limit", "selected": [], "score": None}
    if not edges:
        return {"status": "candidate_optimum", "selected": [], "score": 0}
    pairs = list(combinations(nodes, 2))
    positions = {pair: index for index, pair in enumerate(pairs)}
    cost = np.array([weights.get(pair, 0) for pair in pairs], dtype=float)
    upper = np.array([0 if pair in forbidden else 1 for pair in pairs])
    rows = []
    for a, b, c in combinations(nodes, 3):
        indices = [positions[(a, b)], positions[(a, c)], positions[(b, c)]]
        for negative in indices:
            row = np.zeros(len(pairs))
            row[indices] = 1
            row[negative] = -1
            rows.append(row)
    constraints = [LinearConstraint(np.array(rows), -np.inf, 1)] if rows else []
    bounds = Bounds(np.zeros(len(pairs)), upper)
    integrality = np.ones(len(pairs))

    def optimize(extra):
        return milp(
            -cost,
            integrality=integrality,
            bounds=bounds,
            constraints=[*constraints, *extra],
            options={"time_limit": 5.0, "mip_rel_gap": 0.0},
        )

    def checked(result):
        if result.status != 0 or result.x is None:
            raise ValueError("solver did not prove an optimum")
        rounded = np.rint(result.x)
        if not np.allclose(result.x, rounded, atol=1e-7, rtol=0):
            raise ValueError("nonintegral solution")
        if np.any(rounded < 0) or np.any(rounded > upper):
            raise ValueError("invalid solution bounds")
        if any(row @ rounded > 1 for row in rows):
            raise ValueError("transitivity violation")
        selected = [pair for pair in sorted(weights) if rounded[positions[pair]] == 1]
        score = sum(weights[pair] for pair in selected)
        if result.fun is None or abs(-result.fun - score) > 1e-6:
            raise ValueError("objective mismatch")
        return selected, score

    held = {"status": "held_solver", "selected": [], "score": None}
    try:
        selected, score = checked(optimize([]))
        cut = np.zeros(len(pairs))
        for pair in weights:
            cut[positions[pair]] = 1 if pair in selected else -1
        alternate = optimize([
            LinearConstraint(cost, score, score),
            LinearConstraint(cut, -np.inf, len(selected) - 1),
        ])
        if alternate.status == 2:
            return {"status": "candidate_optimum", "selected": selected, "score": score}
        alternative, other_score = checked(alternate)
        if alternative == selected or other_score != score:
            return held
        return {"status": "held_tie", "selected": [], "score": score}
    except ValueError:
        return held
