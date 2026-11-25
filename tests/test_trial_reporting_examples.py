"""Source-version and synthetic diagram checks; no external guideline text."""
from pathlib import Path
import re

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "docs/trial-reporting/2025-candidate-examples.md"
INDEX = ROOT / "source/index.yml"


def source_entries():
    data = yaml.safe_load(INDEX.read_text(encoding="utf-8"))
    return {item["id"]: item for item in data["items"]}


def flow_counts(text: str):
    # Extract only the explicitly enumerated synthetic n-values from Mermaid nodes.
    section = text.split("```mermaid", 1)[1].split("```", 1)[0]
    return {
        key: int(value)
        for key, value in re.findall(
            r'^\s*([a-z_]+)\["[^"]*?\(n=(\d+)\)"\]', section, re.M
        )
    }


def assert_flow_conservation(counts: dict[str, int]) -> None:
    assert counts["assessed"] == counts["excluded"] + counts["randomised"]
    assert counts["randomised"] == counts["a_alloc"] + counts["b_alloc"]
    for name in ("a", "b"):
        assert counts[f"{name}_alloc"] == (
            counts[f"{name}_received"] + counts[f"{name}_not_received"]
        )
        assert counts[f"{name}_alloc"] == (
            counts[f"{name}_analysed"] + counts[f"{name}_not_analysed"]
        )


def test_trial_guideline_editions_have_correct_publication_dates():
    entries = source_entries()
    assert entries["consort-2025"]["date"] == "2025-04-14"
    assert entries["consort-2025"]["url"] == "https://doi.org/10.1136/bmj-2024-081123"
    assert entries["spirit-2025"]["date"] == "2025-04-28"
    assert entries["spirit-2025"]["url"] == "https://doi.org/10.1136/bmj-2024-081477"
    assert entries["tripod-ai-2024"]["date"] == "2024-04-16"
    assert entries["tripod-ai-2024"]["url"] == "https://doi.org/10.1136/bmj-2023-078378"
    assert "Source-indexed only" in entries["consort-2025"]["notes"]
    assert "Source-indexed only" in entries["spirit-2025"]["notes"]


def test_synthetic_mermaid_flow_conserves_participants():
    text = EXAMPLE.read_text(encoding="utf-8")
    counts = flow_counts(text)
    assert len(counts) == 13
    assert_flow_conservation(counts)
    assert "Text equivalent:" in text
    assert "not official figures" in text.lower()
    assert "can overlap" in text


def test_synthetic_count_mutation_is_rejected():
    text = EXAMPLE.read_text(encoding="utf-8")
    mutated = text.replace('a_received["A received allocated intervention (n=48)"]',
                           'a_received["A received allocated intervention (n=49)"]')
    assert mutated != text
    with pytest.raises(AssertionError):
        assert_flow_conservation(flow_counts(mutated))
