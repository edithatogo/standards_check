"""Typed named-class reference constraints, isolated by exact source context."""

from __future__ import annotations

import hashlib
import re
from collections import Counter

from .source_xml import parse_xml

RELATIONS = {
    "equivalent_class": "{http://www.w3.org/2002/07/owl#}equivalentClass",
    "subclass_of": "{http://www.w3.org/2000/01/rdf-schema#}subClassOf",
    "disjoint_with": "{http://www.w3.org/2002/07/owl#}disjointWith",
}
OWL_CLASS = "{http://www.w3.org/2002/07/owl#}Class"
RDF_ABOUT = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"
RDF_RESOURCE = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"
OBO_PREFIX = "http://purl.obolibrary.org/obo/"


def audit(doc: dict) -> dict:
    """Find classes inheriting both sides of an asserted disjointness.

    Only the selected named axioms are considered. Unsatisfiability is a
    diagnostic, not evidence that an ontology is globally inconsistent.
    """
    if doc["schema_version"] != "dev.standardflow.ontology-reference-assertions.v1":
        raise ValueError("unsupported ontology reference")
    if doc["status"] != "source_asserted_development_reference":
        raise ValueError("unsupported reference authority")
    sources = {row["id"]: row for row in doc["sources"]}
    if not sources or len(sources) != len(doc["sources"]):
        raise ValueError("duplicate or empty source inventory")
    for source in sources.values():
        if not re.fullmatch(r"[0-9a-f]{40}", source["revision"]):
            raise ValueError("source revision must be exact")
        if not re.fullmatch(r"[0-9a-f]{64}", source["sha256"]):
            raise ValueError("source digest must be exact")
    grouped = {key: set() for key in sources}
    counts = Counter()
    for row in doc["assertions"]:
        source, a, relation, b = (
            row["source_id"],
            row["subject"],
            row["relation"],
            row["object"],
        )
        if source not in sources or relation not in RELATIONS or a == b:
            raise ValueError("invalid typed reference")
        if not all(
            re.fullmatch(r"http://purl.obolibrary.org/obo/[A-Za-z]+_[0-9]+", n) for n in (a, b)
        ):
            raise ValueError("named OBO class identifiers required")
        if row["reference_type"] != "asserted_in_pinned_artifact":
            raise ValueError("unknown reference type")
        triple = (a, relation, b)
        if triple in grouped[source]:
            raise ValueError("duplicate named assertion")
        grouped[source].add(triple)
        counts[relation] += 1
    contexts = {}
    for source, triples in grouped.items():
        if not triples or len(triples) > 1000:
            raise ValueError("invalid bounded reference inventory")
        closure = {n: {n} for a, _, b in triples for n in (a, b)}
        disjoint = []
        for a, relation, b in triples:
            if relation == "disjoint_with":
                disjoint.append((a, b))
            else:
                closure[a].add(b)
                if relation == "equivalent_class":
                    closure[b].add(a)
        while True:
            updated = {
                n: set().union(*(closure[p] for p in parents)) for n, parents in closure.items()
            }
            if updated == closure:
                break
            closure = updated
        conflicts = sorted(
            n
            for n, parents in closure.items()
            if any(a in parents and b in parents for a, b in disjoint)
        )
        contexts[source] = {"classes": len(closure), "unsatisfiable_candidates": conflicts}
    return {
        "assertions": sum(counts.values()),
        "relation_counts": dict(sorted(counts.items())),
        "contexts": contexts,
        "costing_equivalence_labels": 0,
        "authority": "source_assertions_only",
    }


def verify_source(doc: dict, source_id: str, raw: bytes) -> int:
    """Replay named assertion extraction against privately supplied exact bytes."""
    audit(doc)
    source = next((row for row in doc["sources"] if row["id"] == source_id), None)
    if source is None or hashlib.sha256(raw).hexdigest() != source["sha256"]:
        raise ValueError("reference source digest mismatch")
    expected = {
        (row["subject"], row["relation"], row["object"])
        for row in doc["assertions"]
        if row["source_id"] == source_id
    }
    actual = set()
    if source["format"] == "rdfxml":
        root = parse_xml(raw, 1_000_000)
        for node in root.findall(OWL_CLASS):
            subject = node.get(RDF_ABOUT)
            for relation, tag in RELATIONS.items():
                for child in node.findall(tag):
                    actual.add((subject, relation, child.get(RDF_RESOURCE)))
    elif source["format"] == "obo":
        predicates = {
            "is_a": "subclass_of",
            "equivalent_to": "equivalent_class",
            "disjoint_from": "disjoint_with",
        }
        for stanza in raw.decode("utf-8").split("\n[Term]\n")[1:]:
            lines = stanza.split("\n[", 1)[0].splitlines()
            identifier = next((line[4:] for line in lines if line.startswith("id: ")), None)
            if identifier is None:
                continue
            subject = OBO_PREFIX + identifier.replace(":", "_")
            for line in lines:
                field, sep, value = line.partition(": ")
                if sep and field in predicates and value:
                    target = value.split()[0]
                    actual.add((subject, predicates[field], OBO_PREFIX + target.replace(":", "_")))
    else:
        raise ValueError("unsupported named assertion artifact")
    if not expected <= actual:
        raise ValueError("pinned reference assertion not found")
    return len(expected)
