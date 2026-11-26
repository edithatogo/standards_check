"""Synthetic contract conservation, not receiving-runtime acceptance."""
from copy import deepcopy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from scripts.qualify_searchright_exchange import (
    digest,
    flow_view,
    pack_view,
    restore,
)

ROOT = Path(__file__).resolve().parents[1]


def fixture(relative):
    return json.loads((ROOT / relative).read_bytes())


def check(relative, value):
    Draft202012Validator(fixture(relative), format_checker=FormatChecker()).validate(value)


def pack():
    source = fixture("contracts/examples/minimal-standard-pack.v1.json")
    second = deepcopy(source["requirements"][0])
    second.update(id="EXAMPLE-1a", display_number="1a", source_anchor="fixture:line:2")
    source["requirements"].append(second)
    return source


def flat_flow():
    return fixture("tests/fixtures/searchright-exchange/complete-flow.json")


def pack_candidate(source):
    return pack_view(source, expected_id="example/minimal-reporting-standard", expected_version="0.1.0")


def flow_candidate(source):
    return flow_view(source, expected_review="fixture:independent-control", template="new_databases_registers")


def test_pack_projection_conserves_identity_order_and_values_with_companion():
    source = pack()
    frozen = deepcopy(source)
    result = pack_candidate(source)
    view = result["view"]
    check("tests/fixtures/searchright-exchange/pack.schema.json", view)
    assert [row["item_id"] for row in view["items"]] == ["EXAMPLE-1", "EXAMPLE-1a"]
    assert view["pack_id"] == source["pack_id"] and view["version"] == source["version"]
    assert view["items"][0]["requirement_summary"] == source["requirements"][0]["normalized_requirement"]
    assert "/authority" in result["companion_fields"]
    assert "/verification" in result["companion_fields"]
    assert "/rights" in result["companion_fields"]
    assert "/requirements/*/source_anchor" in result["companion_fields"]
    assert result["status"] == "candidate_only"
    assert restore(source, result, digest(frozen), pack_candidate) == frozen
    assert source == frozen


@pytest.mark.parametrize("mutation", ["edition", "pack_rights", "item_rights", "unverified", "duplicate", "nonsynthetic"])
def test_pack_boundary_rejects_unsupported_input(mutation):
    source = pack()
    if mutation == "edition":
        source["version"] = "0.2.0"
    elif mutation == "pack_rights":
        source["rights"]["status"] = "review_required"
    elif mutation == "item_rights":
        source["requirements"][0]["rights"] = {**source["rights"], "status": "link_only"}
    elif mutation == "unverified":
        source["verification"]["status"] = "imported_unverified"
    elif mutation == "duplicate":
        source["requirements"].append(deepcopy(source["requirements"][0]))
    else:
        source["authority"]["source_url"] = "https://example.com/real"
    with pytest.raises(ValueError):
        pack_candidate(source)


def test_flow_conserves_explicit_counts_and_keeps_reason_ids_in_companion():
    source = flat_flow()
    check("tests/fixtures/searchright-exchange/flow.schema.json", source)
    original = deepcopy(source)
    result = flow_candidate(source)
    view = result["view"]
    assert view["schema_version"] == "dev.standardflow.prisma-flow.v1"
    assert view["template"] == "new_databases_registers"
    assert view["databases_registers"] == {
        "databases": 8, "registers": 2, "duplicate_records_removed": 1,
        "records_marked_ineligible_by_automation": 1, "records_removed_other_reasons": 0,
        "records_screened": 8, "records_excluded": 3, "reports_sought": 5,
        "reports_not_retrieved": 1, "reports_assessed": 4,
        "reports_excluded": [{"reason": "Synthetic A", "reports": 1}, {"reason": "Synthetic B", "reports": 1}],
        "reports_included": 2,
    }
    assert view["new_included"] == view["total_included"] == {"studies": 1, "reports": 2}
    assert view["other_methods"] is None and view["previous_review"] is None
    assert "/full_text_exclusions/*/reason_id" in result["companion_fields"]
    assert restore(source, result, digest(original), flow_candidate) == original
    assert source == original


@pytest.mark.parametrize("field", list(flat_flow()))
def test_each_missing_flow_field_is_held(field):
    source = flat_flow()
    del source[field]
    with pytest.raises(ValueError):
        flow_candidate(source)


@pytest.mark.parametrize("field,value", [
    ("records_other", 1), ("reports_included", -1), ("records_databases", True),
    ("records_databases", 2**53), ("records_screened", 9), ("reports_sought", 6),
    ("reports_assessed", 3), ("reports_included", 3), ("studies_included", 3),
    ("review_id", "fixture:wrong"),
])
def test_flow_rejects_invalid_or_unrepresentable_values(field, value):
    with pytest.raises(ValueError):
        flow_candidate({**flat_flow(), field: value})


@pytest.mark.parametrize("mutation", ["missing", "zero", "duplicate_id", "duplicate_label"])
def test_flow_exclusion_reason_boundaries(mutation):
    source = flat_flow()
    reasons = source["full_text_exclusions"]
    if mutation == "missing":
        del reasons[0]["reason_id"]
    elif mutation == "zero":
        reasons[0]["count"] = 0
    elif mutation == "duplicate_id":
        reasons[1]["reason_id"] = reasons[0]["reason_id"]
    else:
        reasons[1]["label"] = reasons[0]["label"]
    with pytest.raises(ValueError):
        flow_candidate(source)


def test_companion_and_view_mutations_are_held():
    original = pack()
    pin = digest(original)
    result = pack_candidate(original)
    for field in ("source_sha256", "status", "mapping", "view_sha256", "companion_fields"):
        changed = deepcopy(result)
        changed[field] = None
        with pytest.raises(ValueError):
            restore(original, changed, pin, pack_candidate)
    changed = deepcopy(result)
    changed["view"]["items"].reverse()
    with pytest.raises(ValueError):
        restore(original, changed, pin, pack_candidate)
    changed_source = deepcopy(original)
    changed_source["requirements"][0]["source_anchor"] = "fixture:wrong"
    with pytest.raises(ValueError):
        restore(changed_source, pack_candidate(changed_source), pin, pack_candidate)
    # Restoration is a fresh copy, not a mutation of producer state.
    restored = restore(original, result, pin, pack_candidate)
    restored["requirements"].clear()
    assert len(original["requirements"]) == 2


def test_unknown_template_and_aggregate_overflow_are_held():
    source = flat_flow()
    for template in (None, "updated_databases_registers", "new_databases_registers_other_sources"):
        with pytest.raises(ValueError):
            flow_view(source, expected_review=source["review_id"], template=template)
    source["records_databases"] = 2**53 - 1
    with pytest.raises(ValueError, match="unsafe aggregate"):
        flow_candidate(source)


def test_pack_preserves_explicit_item_rights_and_absent_relationships_in_source():
    source = pack()
    source["requirements"][1]["rights"] = deepcopy(source["rights"])
    source["requirements"][1]["display_number"] = None
    del source["relationships"]
    candidate = pack_candidate(source)
    assert candidate["view"]["items"][1]["label"] == "EXAMPLE-1a"
    assert "/relationships" not in candidate["companion_fields"]
    assert restore(source, candidate, digest(source), pack_candidate) == source
