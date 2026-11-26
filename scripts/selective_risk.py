"""Simultaneous one-sided risk bounds for independent guideline-family units.

This is a candidate threshold evaluator, not a pair-level conformal guarantee.
Family independence, score direction and reference eligibility are external gates.
"""

from __future__ import annotations


def _inventory(rows):
    fields = {"id", "family", "score_bps", "equivalent_candidate", "reference_equivalent"}
    if not isinstance(rows, list) or not 1 <= len(rows) <= 100_000:
        raise ValueError("bounded nonempty sample required")
    for row in rows:
        if not isinstance(row, dict) or set(row) != fields:
            raise ValueError("invalid risk row")
        if any(not isinstance(row[key], str) or not row[key] for key in ("id", "family")):
            raise ValueError("nonempty case and family IDs required")
        if type(row["score_bps"]) is not int or not 0 <= row["score_bps"] <= 10000:
            raise ValueError("invalid score")
        if any(type(row[key]) is not bool for key in fields - {"id", "family", "score_bps"}):
            raise ValueError("explicit reference and candidate labels required")
    ids = {row["id"] for row in rows}
    if len(ids) != len(rows):
        raise ValueError("duplicate case IDs")
    return ids, {row["family"] for row in rows}


def _metrics(rows, threshold, alpha):
    from scipy.stats import beta

    accepted = [
        row for row in rows if row["equivalent_candidate"] and row["score_bps"] >= threshold
    ]
    errors = [row for row in accepted if not row["reference_equivalent"]]
    families = {row["family"] for row in accepted}
    error_families = {row["family"] for row in errors}
    n, k = len(families), len(error_families)
    upper = None
    if n:
        upper = 1.0 if k == n else float(beta.ppf(1 - alpha, k + 1, n - k))
    return {
        "threshold_bps": threshold,
        "total_families": len({row["family"] for row in rows}),
        "accepted_families": n,
        "error_families": k,
        "accepted_pairs": len(accepted),
        "false_equivalences": len(errors),
        "upper_family_risk": upper,
    }


def evaluate(calibration, evaluation, thresholds, *, risk_limit_bps=100, alpha_bps=500):
    """Select by calibration only; report held-out families at the fixed threshold.

    The target is the conditional probability of any false equivalence in a
    family with at least one accepted equivalence. Bonferroni bounds are
    simultaneous over the prespecified grid. They are not pair-level bounds.
    """
    if (
        not isinstance(thresholds, list)
        or not 1 <= len(thresholds) <= 64
        or any(type(t) is not int or not 0 <= t <= 10000 for t in thresholds)
        or len(set(thresholds)) != len(thresholds)
    ):
        raise ValueError("invalid prespecified threshold grid")
    if any(type(x) is not int or not 0 < x < 10000 for x in (risk_limit_bps, alpha_bps)):
        raise ValueError("invalid risk or confidence level")
    cal_ids, cal_families = _inventory(calibration)
    eval_ids, eval_families = _inventory(evaluation)
    if cal_ids & eval_ids or cal_families & eval_families:
        raise ValueError("calibration/evaluation overlap")
    alpha = alpha_bps / 10000
    results = [_metrics(calibration, t, alpha / len(thresholds)) for t in sorted(thresholds)]
    qualified = [
        row
        for row in results
        if row["upper_family_risk"] is not None
        and row["upper_family_risk"] <= risk_limit_bps / 10000
    ]
    selected = qualified[0]["threshold_bps"] if qualified else None
    return {
        "risk_unit": "accepted_guideline_family_any_false_equivalence",
        "risk_limit_bps": risk_limit_bps,
        "alpha_bps": alpha_bps,
        "calibration": results,
        "selected_threshold_bps": selected,
        "evaluation": None if selected is None else _metrics(evaluation, selected, alpha),
        "authority": "advisory_only_requires_independent_reference_and_family_sampling",
    }
