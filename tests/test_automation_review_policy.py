"""Keep native workflow access and dependency proposals free of mandatory review."""

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
AUTOMATIC = {"push", "pull_request", "schedule", "issues", "issue_comment"}


def test_workflows_offer_automatic_execution_and_optional_dispatch():
    paths = sorted((ROOT / ".github/workflows").glob("*.y*ml"))
    assert paths
    for path in paths:
        events = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)["on"]
        assert isinstance(events, dict), path.name
        assert "workflow_dispatch" in events, path.name
        assert AUTOMATIC.intersection(events), path.name


def test_dependency_dashboard_is_not_an_approval_gate():
    config = json.loads((ROOT / "renovate.json").read_text(encoding="utf-8"))
    assert config["dependencyDashboardApproval"] is False
    rules = config["packageRules"]
    assert all(rule.get("dependencyDashboardApproval") is not True for rule in rules)
    major_rules = [rule for rule in rules if "major" in rule.get("matchUpdateTypes", [])]
    assert major_rules
    # Explicit override of the inherited local preset, not just omission.
    assert all(rule["dependencyDashboardApproval"] is False for rule in major_rules)
    assert config["vulnerabilityAlerts"]["dependencyDashboardApproval"] is False
    assert config["prConcurrentLimit"] == 1

