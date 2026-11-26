"""Bounded synthetic controls for ranking and local review groups."""

from copy import deepcopy
from itertools import combinations
import json
import sys

import pytest

from scripts import compose_checklists as composition
from tests.test_compose_checklists import pack



def key(name, item=1):
    return [f"test/{name}/1", "1", f"item:{item}"]


def review(result, members):
    return {
        "pack_snapshot_sha256": result["pack_snapshot_sha256"],
        "scope_sha256": "c" * 64,
        "groups": [{
            "members": members,
            "pairs": [
                {"left": a, "right": b, "relation": "equivalent", "receipt_sha256": "d" * 64}
                for a, b in combinations(members, 2)
            ],
        }],
    }


def test_two_statistical_methods_preserve_every_identity_and_held_row():
    a = pack("a", "Report randomisation sequence.", "Report all outcomes.", "...")
    b = pack("b", "Report randomization sequence.", "Do not report all outcomes.")
    b["requirements"][1]["rights"] = {**b["rights"], "status": "link_only"}
    word = composition.compose([a, b], method="word")
    char = composition.compose([b, a], method="char")
    assert word == composition.compose([a, b])
    assert char == composition.compose([a, b], method="char")
    assert word["requirements"] == char["requirements"]
    assert word["pack_snapshot_sha256"] == char["pack_snapshot_sha256"]
    assert word["method"] != char["method"]
    assert word["candidates"] != char["candidates"]
    assert all(edge["status"] == "candidate_similarity" for edge in char["candidates"])
    assert all(key("b", 2) not in (edge["query"], edge["candidate"]) for edge in char["candidates"])
    assert char["semantic_merges"] == 0
    with pytest.raises(ValueError, match="method"):
        composition.compose([a], method="dense")


def test_reviewed_groups_conserve_all_original_nodes_and_are_order_invariant():
    a, b, c = [pack(name, "Report all outcomes.", "Separate item.") for name in "abc"]
    result = composition.compose([a, b, c])
    decision = review(result, [key("a"), key("b"), key("c")])
    grouped = composition.apply_display_review(result, decision)
    assert grouped["requirements"] == result["requirements"]
    assert grouped["semantic_merges"] == 0
    assert grouped["applicability"] == "not_assessed"
    assert len(grouped["display_groups"]) == 4
    assert grouped["display_groups"][0]["members"] == [key("a"), key("b"), key("c")]
    assert sorted(tuple(k) for g in grouped["display_groups"] for k in g["members"]) == sorted(
        tuple(r["key"]) for r in result["requirements"]
    )
    decision["groups"][0]["members"].reverse()
    decision["groups"][0]["pairs"].reverse()
    assert composition.apply_display_review(result, decision) == grouped
    assert "display_groups" not in result


@pytest.mark.parametrize("defect", ["stale", "scope", "missing_pair", "non_equivalent", "unknown", "duplicate", "held", "duplicate_pair", "bad_hash", "extra_pair"])
def test_review_fails_closed_on_unjustified_grouping(defect):
    a, b, c = [pack(name, "Report all outcomes.", "Separate item.") for name in "abc"]
    if defect == "held":
        c["rights"]["status"] = "review_required"
    result = composition.compose([a, b, c])
    decision = review(result, [key("a"), key("b"), key("c")])
    group = decision["groups"][0]
    if defect == "stale":
        decision["pack_snapshot_sha256"] = "e" * 64
    elif defect == "scope":
        decision["scope_sha256"] = None
    elif defect == "missing_pair":
        group["pairs"].pop()
    elif defect == "non_equivalent":
        group["pairs"][0]["relation"] = "narrower"
    elif defect == "unknown":
        group["members"][0] = key("unknown")
    elif defect == "duplicate":
        decision["groups"].append(deepcopy(group))
    elif defect == "duplicate_pair":
        group["pairs"].append(deepcopy(group["pairs"][0]))
    elif defect == "bad_hash":
        group["pairs"][0]["receipt_sha256"] = "not-a-hash"
    elif defect == "extra_pair":
        group["pairs"][0]["right"] = key("a", 2)
    with pytest.raises(ValueError):
        composition.apply_display_review(result, decision)


@pytest.mark.parametrize("defect", ["fields", "groups_type", "group_fields", "member_type", "pair_type", "key_shape", "singleton", "same_pack", "pair_fields"])
def test_review_shapes_fail_closed(defect):
    result = composition.compose([pack("a", "Report outcomes.", "Other."), pack("b", "Report outcomes.")])
    decision = review(result, [key("a"), key("b")])
    group = decision["groups"][0]
    if defect == "fields":
        decision["extra"] = True
    elif defect == "groups_type":
        decision["groups"] = "groups"
    elif defect == "group_fields":
        group["extra"] = True
    elif defect == "member_type":
        group["members"] = "members"
    elif defect == "pair_type":
        group["pairs"] = "pairs"
    elif defect == "key_shape":
        group["members"][0] = ["a"]
    elif defect == "singleton":
        group["members"].pop()
    elif defect == "same_pack":
        group["members"][1] = key("a", 2)
    elif defect == "pair_fields":
        group["pairs"][0]["extra"] = True
    with pytest.raises(ValueError):
        composition.apply_display_review(result, decision)


def test_cli_review_and_bounded_input(tmp_path, monkeypatch, capsys):
    a, b = pack("a", "Report outcomes."), pack("b", "Report outcomes.")
    result = composition.compose([a, b])
    paths = [tmp_path / name for name in ("a.json", "b.json", "review.json")]
    for path, value in zip(paths, (a, b, review(result, [key("a"), key("b")])), strict=True):
        path.write_text(json.dumps(value))
    monkeypatch.setattr(sys, "argv", ["compose", "--pack", str(paths[0]), "--pack", str(paths[1]), "--method", "char", "--group-review", str(paths[2])])
    composition.main()
    assert len(json.loads(capsys.readouterr().out)["display_groups"]) == 1
    paths[2].write_text(" " * 4097)
    monkeypatch.setattr(composition, "MAX_PACK_BYTES", 4096)
    with pytest.raises(ValueError, match="review byte limit"):
        composition.main()


def test_synthetic_retrieval_development_panel():
    # These analyst-authored labels are development controls, not independent semantics.
    queries = [
        "Report the randomisation sequence generation method.",
        "Describe all prespecified outcomes.",
        "Report the duration of follow-up.",
        "Specify the funding source.",
        "Report the sample size calculation.",
        "Describe the intervention dosage and frequency.",
    ]
    candidates = [
        "Report the randomization sequence generation method.",
        "Describe every prespecified outcome.",
        "Report how long participants were followed.",
        "Identify who funded the study.",
        "Report the sample size calculation.",
        "Describe the intervention dose and administration frequency.",
        "Report the allocation concealment mechanism.",
        "Describe only the primary outcome.",
        "Report the recruitment duration.",
        "Specify the conflict of interest statement.",
        "Report the final sample size without its calculation.",
        "Describe the intervention dosage but not the administration frequency.",
    ]
    a, b = pack("query", *queries), pack("target", *candidates)
    ranks = {}
    for method in ("word", "char"):
        report = composition.compose([a, b], top_k=20, method=method)
        ranks[method] = []
        for i in range(1, 7):
            hits = [edge["candidate"] for edge in report["candidates"] if edge["query"] == key("query", i)]
            ranks[method].append(hits.index(key("target", i)) + 1)
        assert report["semantic_merges"] == 0
    assert ranks == {"word": [1, 1, 7, 8, 1, 2], "char": [1, 1, 2, 2, 1, 1]}
