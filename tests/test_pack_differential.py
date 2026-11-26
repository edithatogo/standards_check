"""Generated pack and arithmetic invariants; hosted CLI tests use the same generator."""

import json
from copy import deepcopy
from pathlib import Path

from hypothesis import given, settings, strategies as st
import pytest

from scripts.orthogonal_experiments import generated_pair
from scripts.qualify_legacy_prisma import validate_pair
from scripts.qualify_pack_differential import KINDS, accepts_python, cases
from scripts.validate_packs import validator

ROOT = Path(__file__).resolve().parents[1]


def test_pack_kind_and_mutation_inventory():
    base = json.loads((ROOT / "contracts/examples/minimal-standard-pack.v1.json").read_text())
    original = deepcopy(base)
    rows = list(cases(base))
    assert len(rows) == len(KINDS) * 4
    assert len({row[0] for row in rows}) == len(rows)
    schema = validator("standard-pack.v1.schema.json")
    for _, pack, expected in rows:
        assert accepts_python(pack, schema) is expected
    assert base == original


@settings(max_examples=64, derandomize=True, deadline=None)
@given(st.tuples(*(st.integers(min_value=1, max_value=10000) for _ in range(4))),
       st.one_of(st.none(), st.integers(min_value=1, max_value=10000)))
def test_generated_prisma_semantics_and_mutation(parts, previous):
    case, legacy = generated_pair(parts, previous)
    validate_pair(case, legacy)
    bad = deepcopy(case)
    bad["rust_input"]["databases_registers"]["records_screened"] += 1
    with pytest.raises(ValueError):
        validate_pair(bad, legacy)
