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


def test_decision_and_reward_failure_paths():
    from scripts.evidence_action_replay import decision, reward, split_document
    import pytest

    def state(word=0.4, char=0.4, a=0, b=0, neg=0, num=0, exact=0, complete=1):
        return (complete, 0, word, char, a, b, neg, num, exact)

    assert decision(state(neg=1)) == "contradictory"
    assert decision(state(num=1)) == "contradictory"
    assert decision(state(a=1)) == "narrower"
    assert decision(state(b=1)) == "broader"
    assert decision(state(word=0.2, char=0.2)) == "indeterminate"
    assert decision(state(word=0.9, char=0.9)) == "equivalent"
    assert decision(state(word=0.9, char=0.2)) == "abstain"
    assert reward(state(exact=1), "contradictory") == -4
    assert reward(state(neg=1), "equivalent") == -1
    assert reward(state(complete=0), "equivalent") == 0
    with pytest.raises(ValueError, match="two nonempty"):
        split_document({"candidate": "one", "id": "single"})


def test_cli_preserves_pinned_fixture_and_rejects_changed_bytes(tmp_path, monkeypatch):
    import json
    from pathlib import Path
    from scripts.evidence_action_replay import main, FIXTURE_SHA

    path = Path("contracts/examples/semantic-reconciliation-synthetic-v1.json")
    target = tmp_path / "result.json"
    monkeypatch.setattr("sys.argv", ["evidence-action", "--fixture", str(path), "--output", str(target)])
    main()
    output = json.loads(target.read_text())
    assert output["report"]["fixture_sha256"] == FIXTURE_SHA
    assert len(output["replay"]) == 360
    assert output["report"]["arms"]["rule"]["correct"] == 18
    changed = tmp_path / "changed.json"
    changed.write_bytes(path.read_bytes() + b"\n")
    monkeypatch.setattr("sys.argv", ["evidence-action", "--fixture", str(changed), "--output", str(target)])
    import pytest
    with pytest.raises(ValueError, match="pinned original"):
        main()
