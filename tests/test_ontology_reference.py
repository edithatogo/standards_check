"""Source assertions are independent of the costing retrieval scores."""

import copy
import hashlib
import json
from pathlib import Path

import pytest

from scripts.ontology_reference import audit, verify_source

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "contracts/analysis/ontology-reference-assertions.v0.1.0.json"


def test_named_reference_assertions_and_release_contexts():
    doc = json.loads(SEED.read_text())
    result = audit(doc)
    assert result["assertions"] == 18
    assert result["relation_counts"] == {"equivalent_class": 3, "subclass_of": 9, "disjoint_with": 6}
    assert len(result["contexts"]) == 3
    assert not any(row["unsatisfiable_candidates"] for row in result["contexts"].values())
    assert result["costing_equivalence_labels"] == 0


def test_named_subclass_disjointness_inheritance_detects_conflict():
    doc = json.loads(SEED.read_text())
    source = doc["assertions"][0]["source_id"]
    template = doc["assertions"][0]
    doc["assertions"].append({
        **template, "source_id": source,
        "subject": "http://purl.obolibrary.org/obo/BFO_0000015",
        "object": "http://purl.obolibrary.org/obo/BFO_0000002",
        "relation": "subclass_of",
    })
    result = audit(doc)
    assert "http://purl.obolibrary.org/obo/BFO_0000015" in result["contexts"][source]["unsatisfiable_candidates"]
    bad = copy.deepcopy(doc)
    bad["assertions"][0]["relation"] = "similar_to"
    with pytest.raises(ValueError):
        audit(bad)


def test_exact_artifact_digest_is_required():
    doc = json.loads(SEED.read_text())
    with pytest.raises(ValueError):
        verify_source(doc, "obi-core", b"not the source")

@pytest.mark.parametrize("fmt,raw", [
    ("obo", b"format-version: 1.2\n\n[Term]\nid: OBI:1\nis_a: OBI:2\n"),
    ("rdfxml", b'<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
     b'xmlns:owl="http://www.w3.org/2002/07/owl#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">'
     b'<owl:Class rdf:about="http://purl.obolibrary.org/obo/OBI_1">'
     b'<rdfs:subClassOf rdf:resource="http://purl.obolibrary.org/obo/OBI_2"/>'
     b'</owl:Class></rdf:RDF>'),
])
def test_replay_exact_synthetic_assertion_and_reject_missing_triple(fmt, raw):
    doc = json.loads(SEED.read_text())
    doc["sources"] = [{
        "id": "fixture", "format": fmt, "revision": "a" * 40,
        "sha256": hashlib.sha256(raw).hexdigest(),
    }]
    doc["assertions"] = [{
        "source_id": "fixture", "subject": "http://purl.obolibrary.org/obo/OBI_1",
        "object": "http://purl.obolibrary.org/obo/OBI_2", "relation": "subclass_of",
        "reference_type": "asserted_in_pinned_artifact",
    }]
    assert verify_source(doc, "fixture", raw) == 1
    doc["assertions"][0]["object"] = "http://purl.obolibrary.org/obo/OBI_3"
    with pytest.raises(ValueError, match="not found"):
        verify_source(doc, "fixture", raw)

def test_reference_rejects_lookalike_hostname():
    doc = json.loads(SEED.read_text())
    doc["assertions"][0]["subject"] = "http://purlXobolibrary.org/obo/OBI_1"
    with pytest.raises(ValueError, match="named OBO"):
        audit(doc)
