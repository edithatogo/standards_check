"""Offline split-conformal rank oracle for advisory relation triage.

Callers must freeze the score function, complete label universe, independent
calibration/reference data and exchangeability unit. This module cannot verify
those prerequisites or authorize semantic equivalence, rights or pack admission.
"""

from __future__ import annotations

import math
from bisect import bisect_left
from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class PredictionSet:
    """Deterministic label set and finite-rank resolution diagnostic."""

    labels: tuple[str, ...]
    underpowered_labels: tuple[str, ...]

    @property
    def candidate(self) -> str | None:
        """Return an advisory singleton only when all strata resolve alpha."""
        if len(self.labels) == 1 and not self.underpowered_labels:
            return self.labels[0]
        return None


def _valid_score(score: float) -> bool:
    return not isinstance(score, bool) and math.isfinite(score)


def prediction_set(
    calibration: Sequence[tuple[str, float]],
    scores: Mapping[str, float],
    *,
    alpha_basis_points: int,
    mondrian: bool = False,
) -> PredictionSet:
    """Include labels with conservative rank p-value strictly above alpha.

    Larger scores are less conforming. For each label, count calibration true-
    label scores >= its candidate score, add one, and divide by n+1. Class-
    conditional (Mondrian) mode uses only calibration scores of that label.
    Integer comparison avoids floating-point alpha rounding. Empty or small
    strata cannot exclude a label at the requested rank resolution and force
    advisory abstention, even if the resulting set is a singleton.
    """
    if type(alpha_basis_points) is not int or not 0 < alpha_basis_points < 10_000:
        raise ValueError("alpha must be an integer from 1 to 9999 basis points")
    if not scores or any(not label or not _valid_score(score) for label, score in scores.items()):
        raise ValueError("nonempty labels and finite nonconformity scores required")
    pooled: list[float] = []
    strata: dict[str, list[float]] = {label: [] for label in scores}
    for label, score in calibration:
        if label not in strata or not _valid_score(score):
            raise ValueError("calibration label or nonconformity score is invalid")
        pooled.append(score)
        strata[label].append(score)
    pooled.sort()
    for stratum in strata.values():
        stratum.sort()
    included: list[str] = []
    underpowered: list[str] = []
    for label in sorted(scores):
        reference = strata[label] if mondrian else pooled
        n = len(reference)
        cutoff = alpha_basis_points * (n + 1)
        if cutoff < 10_000:
            underpowered.append(label)
        numerator = 1 + n - bisect_left(reference, scores[label])
        if 10_000 * numerator > cutoff:
            included.append(label)
    return PredictionSet(tuple(included), tuple(underpowered))
