"""Exercise the analytical export's admission boundaries and byte-bound CLI."""

from copy import deepcopy
import hashlib
import json
import subprocess
import sys

from hypothesis import given, settings, strategies as st
import polars as pl
import pytest

from scripts import survey_projections as projection


def inputs(count=1):
    catalogue = {
        "source_revision": "a" * 40,
        "published_count": 1,
        "guidelines": [
            {
                "id": "equator:example",
                "page_url": "https://equator-network.org/reporting-guidelines/example/",
                "source_blob_sha": "b" * 40,
                "metadata_status": "extracted_unverified",
            }
        ],
    }
    survey = {
        "source_revision": "a" * 40,
        "summary": {"canonical_packs_promoted": 0, "published_count": 1},
        "records": [
            {"id": "equator:example", "source_blob_sha": "b" * 40, "status": "oa_xml_candidate"}
        ],
        "priority_articles": [
            {
                "edition": "example-1",
                "status": "expected_numbered_rows_observed",
                "source_sha256": "d" * 64,
                "expected_rows": count,
                "matched_rows": count,
                "canonical_packs_promoted": 0,
                "tables": [
                    {
                        "table_id": "t1",
                        "items": [
                            {
                                "item_id": str(i),
                                "source_anchor": f"t1:{i}",
                                "normalized_text_sha256": hashlib.sha256(
                                    str(i).encode()
                                ).hexdigest(),
                            }
                            for i in range(count)
                        ],
                    }
                ],
            }
        ],
    }
    retrospective = {"canonical_packs_promoted": 0, "findings": []}
    return catalogue, survey, retrospective


@settings(max_examples=64, derandomize=True)
@given(count=st.integers(1, 40), prose=st.text(max_size=250))
def test_unreviewed_prose_never_changes_the_text_free_projection(count, prose):
    catalogue, survey, retrospective = inputs(count)
    expected = projection.project_survey(catalogue, survey, retrospective)
    for item in survey["priority_articles"][0]["tables"][0]["items"]:
        item["text"] = prose
        item["unreviewed_claim"] = "cleared for use"
    actual = projection.project_survey(catalogue, survey, retrospective)
    assert actual == expected
    projection.validate(actual)
    assert all(item["disposition"] == "held_review" for item in actual["acquisition_items"])
    # A successful extraction never authorizes acquisition rights.
    assert actual["acquisitions"][0]["rights_status"] == "unassessed"


@pytest.mark.parametrize(
    "mutation, diagnostic",
    [
        (lambda c, s, r: c["guidelines"].append(deepcopy(c["guidelines"][0])), "duplicate"),
        (
            lambda c, s, r: s["priority_articles"].append(deepcopy(s["priority_articles"][0])),
            "duplicate",
        ),
        (
            lambda c, s, r: s["priority_articles"][0].update(canonical_packs_promoted=1),
            "cannot promote",
        ),
        (
            lambda c, s, r: s["priority_articles"][0]["tables"][0]["items"][0].update(
                normalized_text_sha256="bad"
            ),
            "fingerprint",
        ),
        (
            lambda c, s, r: c["guidelines"][0].update(
                page_url="https://untrusted.invalid/example/"
            ),
            "directory identity",
        ),
        (lambda c, s, r: r.update(canonical_packs_promoted=1), "admission boundary"),
    ],
)
def test_projection_refuses_ambiguous_identity_or_implicit_admission(mutation, diagnostic):
    catalogue, survey, retrospective = inputs()
    mutation(catalogue, survey, retrospective)
    with pytest.raises(ValueError, match=diagnostic):
        projection.project_survey(catalogue, survey, retrospective)


@pytest.mark.parametrize(
    "table, key, value, diagnostic",
    [
        ("catalogue_identity", "rights_status", "cleared", "authorize use"),
        ("catalogue_identity", "disposition", "approved", "authorize use"),
        ("catalogue_identity", "lookup_status", "identifier_conflict", "authorize use"),
        ("acquisitions", "rights_status", "cleared", "unassessed"),
        ("acquisitions", "disposition", "approved", "remain held"),
        ("acquisitions", "expected_rows", -1, "count mismatch"),
        ("acquisitions", "matched_rows", None, "count mismatch"),
        ("acquisitions", "source_sha256", None, "fingerprint"),
        ("acquisition_items", "edition", "unknown", "unbound"),
        ("acquisition_items", "source_anchor", "", "item evidence"),
        ("acquisition_items", "table_id", "", "item evidence"),
        ("acquisition_items", "fingerprint", "invalid", "item evidence"),
    ],
)
def test_serialized_projection_cannot_escalate_or_lose_its_denominator(
    table, key, value, diagnostic
):
    tables = projection.project_survey(*inputs())
    tables[table][0][key] = value
    with pytest.raises(ValueError, match=diagnostic):
        projection.validate(tables)


def write_inputs(root):
    values = dict(zip(("catalogue", "survey", "retrospective"), inputs(), strict=True))
    survey_raw = json.dumps(values["survey"]).encode()
    values["retrospective"]["receipt_sha256"] = hashlib.sha256(survey_raw).hexdigest()
    for name, value in values.items():
        (root / f"{name}.json").write_text(json.dumps(value))
    return [argument for name in values for argument in (f"--{name}", str(root / f"{name}.json"))]


@pytest.mark.parametrize("origin", ["scheduled_or_live", "historical_replay"])
def test_cli_binds_all_three_inputs_and_round_trips_typed_parquet(tmp_path, origin):
    arguments = write_inputs(tmp_path)
    output = tmp_path / "export"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.survey_projections",
            *arguments,
            "--output",
            str(output),
            "--revision",
            "e" * 40,
            "--origin",
            origin,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["producer_revision"] == "e" * 40
    assert manifest["origin"] == origin
    assert manifest["canonical_packs_promoted"] == 0
    for name in ("catalogue", "survey", "retrospective"):
        assert (
            manifest["input_sha256s"][name]
            == hashlib.sha256((tmp_path / f"{name}.json").read_bytes()).hexdigest()
        )
    tables = {
        name: pl.read_parquet(output / f"{name}.parquet").to_dicts() for name in projection.SCHEMAS
    }
    projection.validate(tables)
    assert {name: len(rows) for name, rows in tables.items()} == json.loads(result.stdout)


@pytest.mark.parametrize("defect", ["revision", "unbound_bytes", "oversized"])
def test_cli_fails_without_publishing_a_manifest_for_untrusted_inputs(tmp_path, defect):
    arguments = write_inputs(tmp_path)
    revision = "main" if defect == "revision" else "e" * 40
    if defect == "unbound_bytes":
        with (tmp_path / "survey.json").open("a") as stream:
            stream.write("\n")
    if defect == "oversized":
        with (tmp_path / "survey.json").open("wb") as stream:
            stream.truncate(30_000_001)
    output = tmp_path / "export"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.survey_projections",
            *arguments,
            "--output",
            str(output),
            "--revision",
            revision,
            "--origin",
            "historical_replay",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert not (output / "manifest.json").exists()
