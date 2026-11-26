"""Characterize the pinned consumer boundary, not a live integration."""

import copy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = ROOT / "tests/fixtures/searchright-exchange"
PINS = {
    "pack.schema.json": "33ba981156e62f346a8fbbc5e801d72695a29de765c7b3409609642fbc7a7359",
    "flow.schema.json": "541c777d68190cf31def9b7f890611bb1b3afc9b474853bab417547910d4e332",
    "review-flow.json": "6841b0d9cea51e5319b20d259d33ba9b9649283847a423e35ca5a8092344e3d0",
}


def snapshot(name):
    raw = (SNAPSHOTS / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PINS[name]
    return json.loads(raw)


def validator(schema):
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_pack_schema_rejects_direct_native_pack_and_accepts_consumer_control():
    schema = snapshot("pack.schema.json")
    check = validator(schema)
    pack = json.loads((ROOT / "contracts/examples/minimal-standard-pack.v1.json").read_bytes())
    assert not check.is_valid(pack)
    assert {"authority", "verification", "rights", "requirements"}.isdisjoint(
        schema["properties"]
    )
    consumer = {
        "schema_version": "org.searchright.standard-pack.v1",
        "pack_id": "fixture/example",
        "family": {"custom": "synthetic"},
        "version": "0.1.0",
        "source": "Synthetic source",
        "provenance_note": "Test only",
        "items": [{
            "item_id": "EXAMPLE-1",
            "label": "Example",
            "requirement_summary": "Describe the method.",
            "scope": "reporting",
            "crosswalks": [],
        }],
    }
    check.validate(consumer)
    # The consumer's strict object cannot carry the native structured rights record.
    consumer["rights"] = pack["rights"]
    assert not check.is_valid(consumer)


def test_envelope_validity_does_not_qualify_payload_or_provenance():
    envelope = snapshot("review-flow.json")
    schema = json.loads((ROOT / "schemas/ecosystem-evidence.v1.schema.json").read_bytes())
    check = validator(schema)
    check.validate(envelope)
    assert envelope["artifact_provenance"]["kind"] == "pull_request_head"
    assert envelope["artifact_provenance"]["immutable"] is False
    flow = validator(snapshot("flow.schema.json"))
    assert not flow.is_valid(envelope["payload"]["counts"])
    for key, value in (("authority", "advisory"), ("producer", "standardflow")):
        altered = {**envelope, key: value}
        assert not check.is_valid(altered)
    altered = copy.deepcopy(envelope)
    altered["artifact_provenance"]["immutable"] = True
    assert not check.is_valid(altered)


def test_count_fixture_has_nine_missing_required_fields_and_two_extra_fields():
    counts = snapshot("review-flow.json")["payload"]["counts"]
    schema = snapshot("flow.schema.json")
    assert set(schema["required"]) - counts.keys() == {
        "schema_version", "review_id", "records_databases", "records_registers",
        "records_other", "automation_removed", "other_removed",
        "full_text_exclusions", "reports_included",
    }
    assert counts.keys() - schema["properties"].keys() == {
        "records_identified", "reports_excluded",
    }
    # Independently authored positive control, not a repair of the upstream fixture.
    complete = {
        "schema_version": "org.searchright.prisma-flow.v1",
        "review_id": "fixture:independent-control",
        "records_databases": 8,
        "records_registers": 2,
        "records_other": 0,
        "duplicates_removed": 1,
        "automation_removed": 1,
        "other_removed": 0,
        "records_screened": 8,
        "records_excluded": 3,
        "reports_sought": 5,
        "reports_not_retrieved": 1,
        "reports_assessed": 4,
        "full_text_exclusions": [{"reason_id": "r1", "label": "Synthetic", "count": 2}],
        "studies_included": 1,
        "reports_included": 2,
    }
    check = validator(schema)
    check.validate(complete)
    for key in schema["required"]:
        missing = {k: v for k, v in complete.items() if k != key}
        assert not check.is_valid(missing), key
    assert not check.is_valid({**complete, "reports_included": -1})
    assert not check.is_valid({**complete, "records_identified": 10})
