"""Synthetic differential cases and predeclared calibration comparison.

Independent source/reference eligibility is a caller obligation. No admission.
"""

from __future__ import annotations

import math

from .conformal_triage import prediction_set

LABELS = ("broader", "contradictory", "equivalent", "indeterminate", "narrower")


def generated_pair(parts: tuple, previous: int | None) -> tuple[dict, dict]:
    """Construct independent synthetic stage partitions for the legacy parity runner."""
    if len(parts) != 4 or any(type(n) is not int or not 1 <= n <= 10000 for n in parts):
        raise ValueError("four positive bounded integer partitions required")
    if previous is not None and (type(previous) is not int or not 1 <= previous <= 10000):
        raise ValueError("positive previous review count required")
    duplicates, excluded, reports_excluded, included = parts
    assessed = reports_excluded + included
    screened = excluded + assessed
    identified = duplicates + screened
    updated = previous is not None
    old = previous or 0
    total = old + included
    identifier = "generated-" + "-".join(map(str, (*parts, old)))
    counts = {
        "identified": identified,
        "duplicates": duplicates,
        "screened": screened,
        "records_excluded": excluded,
        "assessed": assessed,
        "reports_excluded": reports_excluded,
        "new_studies": included,
        "previous_studies": old,
        "total_studies": total,
    }
    prefix = "new_" if updated else ""
    legacy_counts = {
        "records_identified": identified,
        "records_after_duplicates_removed": screened,
        "records_screened": screened,
        "records_excluded": excluded,
        "full_text_articles_assessed": assessed,
        "full_text_articles_excluded": reports_excluded,
        "studies_included": included,
    }
    legacy = {
        "diagram_type": "PRISMA_2020_UPDATED" if updated else "PRISMA",
        **{prefix + k: v for k, v in legacy_counts.items()},
    }
    if updated:
        legacy.update(previous_studies=old, total_studies_included=total)
    conditions = dict.fromkeys(
        (
            "database_records_only",
            "duplicates_are_only_prescreen_removal",
            "all_sought_reports_retrieved",
            "legacy_full_text_articles_are_reports",
            "one_report_per_included_study",
            "exclusion_reason_partition_supplied",
        ),
        True,
    )
    if updated:
        conditions["previous_and_new_studies_disjoint"] = True
    flow = {
        "schema_version": "dev.standardflow.prisma-flow.v1",
        "review_id": identifier,
        "template": "updated_databases_registers" if updated else "new_databases_registers",
        "databases_registers": {
            "databases": identified,
            "registers": 0,
            "duplicate_records_removed": duplicates,
            "records_marked_ineligible_by_automation": 0,
            "records_removed_other_reasons": 0,
            "records_screened": screened,
            "records_excluded": excluded,
            "reports_sought": assessed,
            "reports_not_retrieved": 0,
            "reports_assessed": assessed,
            "reports_excluded": [{"reason": "Synthetic exclusion", "reports": reports_excluded}],
            "reports_included": included,
        },
        "other_methods": None,
        "previous_review": {"studies": old, "reports": old} if updated else None,
        "new_included": {"studies": included, "reports": included},
        "total_included": {"studies": total, "reports": total},
    }
    return {"id": identifier, "conditions": conditions, "expected_counts": counts, "rust_input": flow}, legacy


def compare(calibration: list[dict], evaluation: list[dict], *, alpha: int) -> dict:
    """Compare minimum-score classification and conformal sets on identical cases."""
    if not calibration or not evaluation or len(calibration) + len(evaluation) > 10000:
        raise ValueError("nonempty bounded disjoint samples required")
    rows = calibration + evaluation
    if any(
        not row["id"]
        or not row["family"]
        or row["reference"] not in LABELS
        or set(row["scores"]) != set(LABELS)
        or any(isinstance(v, bool) or not math.isfinite(v) for v in row["scores"].values())
        for row in rows
    ):
        raise ValueError("complete finite five-label rows required")
    if len({row["id"] for row in rows}) != len(rows) or {row["family"] for row in calibration} & {
        row["family"] for row in evaluation
    }:
        raise ValueError("case or guideline family overlap")
    reference = [(row["reference"], row["scores"][row["reference"]]) for row in calibration]
    result = {
        method: dict.fromkeys(
            (
                "accepted",
                "abstained",
                "errors",
                "equivalent_predictions",
                "false_equivalences",
                "set_misses",
            ),
            0,
        )
        for method in ("baseline", "split", "mondrian")
    }
    disagreements = 0
    for row in evaluation:
        scores, truth = row["scores"], row["reference"]
        baseline = [label for label in LABELS if scores[label] == min(scores.values())]
        predictions = {"baseline": (baseline, baseline[0] if len(baseline) == 1 else None)}
        for method in ("split", "mondrian"):
            mondrian = method == "mondrian"
            prediction = prediction_set(
                reference, scores, alpha_basis_points=alpha, mondrian=mondrian
            )
            # Independent direct count, not the production sorted-rank implementation.
            expected = []
            for label in LABELS:
                sample = [score for target, score in reference if not mondrian or target == label]
                if 10_000 * (1 + sum(score >= scores[label] for score in sample)) > alpha * (
                    len(sample) + 1
                ):
                    expected.append(label)
            disagreements += tuple(expected) != prediction.labels
            predictions[method] = (prediction.labels, prediction.candidate)
        for method, (labels, candidate) in predictions.items():
            metrics = result[method]
            metrics["set_misses"] += truth not in labels
            metrics["accepted"] += candidate is not None
            metrics["abstained"] += candidate is None
            metrics["errors"] += candidate is not None and candidate != truth
            metrics["equivalent_predictions"] += candidate == "equivalent"
            metrics["false_equivalences"] += candidate == "equivalent" and truth != "equivalent"
    return {
        **result,
        "calibration_cases": len(calibration),
        "test_cases": len(evaluation),
        "alpha_basis_points": alpha,
        "rank_disagreements": disagreements,
    }


def synthetic_comparison() -> dict:
    """Fixed fabricated score controls, not independent empirical model calibration."""

    def make_rows(split, count):
        rows = []
        for label in LABELS:
            for i in range(count):
                scores = dict.fromkeys(LABELS, 0.9)
                scores[label] = (i % 50) / 100
                if split == "evaluation" and i % 3 == 0:
                    scores[label] = 0.6
                    scores["equivalent" if label != "equivalent" else "narrower"] = 0.2
                elif split == "evaluation" and i % 3 == 1:
                    scores["equivalent" if label != "equivalent" else "narrower"] = 0.3
                rows.append(
                    {
                        "id": f"{split}-{label}-{i}",
                        "family": f"{split}-{label}",
                        "reference": label,
                        "scores": scores,
                    }
                )
        return rows

    return {
        "scope": "synthetic_only",
        **compare(make_rows("calibration", 99), make_rows("evaluation", 10), alpha=100),
    }
