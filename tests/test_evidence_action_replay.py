"""Evidence-action replay remains advisory and family-separated."""
from scripts.evidence_action_replay import ACTIONS, build_replay, experiment, observe


def case(key, family, split, source, candidate):
    return dict(id=key, family=family, split=split, source=source, candidate=candidate,
                forward="entailment", reverse="entailment")


def fixture():
    cases = []
    for split, family in [("dev", "one"), ("test", "two")]:
        cases += [case(f"{family}-{i}", family, split, a, b) for i, (a, b) in enumerate([
            ("Report the outcome and dates.", "Report the outcome and dates."),
            ("Describe the intervention methods.", "Describe the intervention methods."),
            ("Report the trial funding source.", "Report the trial funding source."),
        ])]
    return cases


def test_replay_executes_every_feasible_action_and_referrals_do_not_resolve():
    rows = build_replay(fixture())
    assert rows
    for row in rows:
        assert set(row["transitions"]) == (set(ACTIONS) - set(row["history"]) if len(row["history"]) < 2 else set()) | {"abstain", "review"}
        assert row["transitions"]["review"]["referrals"] == 1
        assert row["transitions"]["review"]["review_outcome"] is None
        assert row["transitions"]["review"]["resolved"] is False
        assert row["transitions"]["abstain"]["resolved"] is False


def test_observations_do_not_include_references_or_hidden_fragments():
    rows = build_replay(fixture())
    for row in rows:
        observation = observe(row)
        assert len(observation) == 9
        changed = {**row, "reference": "contradictory", "transitions": {}}
        assert observe(changed) == observation


def test_experiment_evaluates_observed_outcomes_at_matched_workload():
    report = experiment(fixture())
    arms = report["arms"]
    assert set(arms) == {"rule", "forecast", "imagined_critic", "observed_critic"}
    assert len({a["retrieval_calls"] for a in arms.values()}) == 1
    assert len({a["referrals"] for a in arms.values()}) == 1
    for arm in arms.values():
        assert arm["correct"] <= arm["n"] - arm["referrals"]
        assert arm["review_resolved"] == 0
        assert arm["n"] == 3
    assert report["forecast"]["n"] > 0


def test_test_family_labels_cannot_change_policy_actions():
    cases = fixture()
    changed = [{**c, "forward": "contradiction", "reverse": "contradiction"}
               if c["split"] == "test" else c for c in cases]
    first = experiment(cases)
    second = experiment(changed)
    for arm in first["details"]:
        for key, d in first["details"][arm].items():
            other = second["details"][arm][key]
            assert [e["action"] for e in d["trace"]] == [e["action"] for e in other["trace"]]
            assert d["prediction"] == other["prediction"]
            assert d["referral"] == other["referral"]


def test_family_overlap_rejected():
    import pytest

    cases = fixture()
    cases[-1]["family"] = "one"
    with pytest.raises(ValueError, match="family-level split"):
        build_replay(cases)


def test_replay_monotone_evidence_and_fixed_rerank_pool():
    rows = build_replay(fixture())
    lookup = {(row["id"], tuple(row["history"])): row for row in rows}
    for row in rows:
        for action, edge in row["transitions"].items():
            if action in ACTIONS:
                nxt = lookup[(row["id"], tuple(edge["next"]))]
                assert nxt["evidence"] == {**row["evidence"], **edge["new_evidence"]}
                assert edge["retrieval_calls"] == 1
                if action == "deep_rerank":
                    assert set(edge["ranking"]) <= set(row["pool"])
                    assert edge["reranks"] == 1
