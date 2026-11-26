"""Synthetic parser and byte-preservation controls."""

import pytest

from scripts.markdown_normalization import normalize

TICK = chr(96)


def code(text):
    return TICK + text + TICK


def test_units_dois_and_unchanged_bytes():
    original = (
        "# Synthetic\n\n"
        + "Dose " + code("unit:µg") + "; citation " + code("doi:https://doi.org/10.1234/AbC")
        + ".\n\n<!-- keep  spaces -->\n"
        + "[link](https://example.invalid)\n"
    )
    expected = original.replace("unit:µg", "unit:ug").replace("doi:https://doi.org/", "doi:")
    result = normalize(original.encode())
    assert result["status"] == "normalized_in_scope"
    assert result["edited"] == 2
    assert result["output"] == expected.encode()
    assert normalize(result["output"])["status"] == "unchanged"


def test_unknown_or_duplicate_markers_hold_without_partial_rewrite():
    for text in (
        code("unit:µg") + " " + code("unit:unknown"),
        code("unit:µg") + " " + code("unit:µg"),
        code("unit:µg") + "\n\n<!-- " + code("unit:µg") + " -->",
        TICK * 2 + "unit:µg" + TICK * 2,
        code("doi:https://not-doi.invalid/10.1234/a"),
    ):
        raw = text.encode()
        result = normalize(raw)
        assert result["status"].startswith("held_")
        assert result["output"] == raw
        assert result["edited"] == 0


def test_fenced_examples_and_plain_prose_are_not_normalized():
    raw = (TICK * 3 + "\n" + code("unit:µg") + "\n" + TICK * 3 + "\n\nunit:µg\n").encode()
    result = normalize(raw)
    assert result["status"] == "unchanged"
    assert result["output"] == raw
    with pytest.raises(UnicodeDecodeError):
        normalize(b"\xff")
