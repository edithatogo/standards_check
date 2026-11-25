"""Synthetic grammatical annotations test role invariants, not parser qualification."""

from dataclasses import dataclass, field

from hypothesis import given, settings, strategies as st
import pytest

from scripts import classical_linguistic_nlp as linguistic


@dataclass
class Token:
    lemma_: str
    dep_: str = ""
    pos_: str = "NOUN"
    children: tuple = field(default_factory=tuple)
    conjuncts: tuple = field(default_factory=tuple)


def verb(*arguments):
    return Token("report", "ROOT", "VERB", arguments)


@settings(max_examples=64, derandomize=True)
@given(
    actor=st.from_regex(r"[a-z]{2,20}", fullmatch=True),
    patient=st.from_regex(r"[a-z]{2,20}", fullmatch=True),
)
def test_explicit_active_and_passive_roles_agree_without_inventing_an_actor(actor, patient):
    active = linguistic.predicate_arguments([verb(Token(actor, "nsubj"), Token(patient, "obj"))])
    passive = linguistic.predicate_arguments(
        [verb(Token(patient, "nsubjpass"), Token("by", "agent", children=(Token(actor, "pobj"),)))]
    )
    assert active == passive
    omitted = linguistic.predicate_arguments([verb(Token(patient, "nsubjpass"))])
    assert all(role[0] != "actor" for role in omitted[0]["arguments"])
    changed = linguistic.predicate_arguments(
        [verb(Token("different-" + actor, "nsubj"), Token(patient, "obj"))]
    )
    assert changed != active


@pytest.mark.parametrize(
    "dependency, role",
    [
        ("csubj", "actor"),
        ("obl:agent", "actor"),
        ("csubjpass", "patient"),
        ("nsubj:pass", "patient"),
        ("dobj", "patient"),
        ("iobj", "recipient"),
        ("dative", "recipient"),
        ("attr", "complement"),
        ("oprd", "complement"),
    ],
)
def test_role_vocabulary_preserves_patient_recipient_and_complement(dependency, role):
    report = linguistic.predicate_arguments([Token("ignored"), verb(Token("evidence", dependency))])
    assert len(report) == 1
    assert report[0]["arguments"][0][0] == role


def test_modifiers_and_conjunctions_are_lexical_but_determiners_are_not():
    red = Token("red", "amod")
    first = Token("outcome", "obj", children=(red, Token("the", "det")), conjuncts=(Token("harm"),))
    reordered = Token(
        "outcome", "obj", children=(Token("a", "det"), red), conjuncts=(Token("harm"),)
    )
    assert linguistic.predicate_arguments([verb(first)]) == linguistic.predicate_arguments(
        [verb(reordered)]
    )
    other = Token("outcome", "obj", children=(Token("blue", "amod"),), conjuncts=(Token("harm"),))
    assert linguistic.predicate_arguments([verb(first)]) != linguistic.predicate_arguments(
        [verb(other)]
    )
    assert len(linguistic.predicate_arguments([verb(first)])[0]["arguments"]) == 2


def test_unbalanced_grouping_and_token_overflow_remain_explicit():
    for value in ("(A and B", "A and B)"):
        assert linguistic.logic_grouping(value)["balanced"] is False
    assert (
        linguistic.compare(" ".join(["token"] * 1025), "Report evidence.")["status"] == "held_input"
    )
