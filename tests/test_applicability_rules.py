import copy
import unittest

from scripts.applicability_rules import evaluate

ANCHOR = {"source_id": "synthetic", "sha256": "a" * 64, "locator": "fixture:1"}


def fact(key, literal):
    return {"id": key, "literal": literal, "anchor": ANCHOR}


def rule(key, head, *body):
    return {"id": key, "head": head, "body": list(body), "anchor": ANCHOR}


def decision(key, obligation, action, priority, *body):
    return {
        "id": key, "obligation": obligation, "action": action,
        "priority": priority, "body": list(body), "anchor": ANCHOR,
    }


def contract():
    return {
        "schema_version": "dev.standardflow.applicability-rules.v1",
        "facts": [fact("f1", "clustered"), fact("f2", "trial")],
        "rules": [rule("r2", "extension", "eligible"), rule("r1", "eligible", "trial", "clustered")],
        "decisions": [decision("base", "item", "require", 0, "trial"),
                      decision("ext", "item", "exclude", 1, "extension")],
    }


class ApplicabilityRuleTests(unittest.TestCase):
    def test_recursive_closure_and_explicit_precedence(self):
        result = evaluate(contract())
        row = result["obligations"]["item"]
        self.assertEqual(row["status"], "not_applicable")
        self.assertEqual(row["rules"], ["ext"])
        self.assertEqual(row["support"], ["f1", "f2", "r1", "r2"])
        self.assertEqual(result["authority"], "advisory_only")

    def test_unknown_extension_cannot_exclude_or_fall_through(self):
        doc = contract()
        doc["facts"].pop(0)
        self.assertEqual(evaluate(doc)["obligations"]["item"]["status"], "unknown")
        doc["facts"].append(fact("f3", "!extension"))
        self.assertEqual(evaluate(doc)["obligations"]["item"]["status"], "required")

    def test_conflict_taints_recursive_derivation(self):
        doc = contract()
        doc["facts"].append(fact("f3", "!clustered"))
        result = evaluate(doc)
        self.assertEqual(result["obligations"]["item"]["status"], "held_conflict")
        self.assertEqual(result["conflicted_atoms"], ["clustered"])
        self.assertIn("extension", result["tainted_atoms"])

    def test_equal_priority_disagreement_and_missing_anchor_hold(self):
        doc = contract()
        doc["decisions"].append(decision("rival", "item", "require", 1, "extension"))
        self.assertEqual(evaluate(doc)["obligations"]["item"]["status"], "held_conflict")
        bad = copy.deepcopy(doc)
        bad["rules"][0]["anchor"]["sha256"] = "unverified"
        with self.assertRaises(ValueError):
            evaluate(bad)

    def test_cycle_without_seed_does_not_manufacture_facts(self):
        doc = contract()
        doc["facts"] = []
        doc["rules"] = [rule("r1", "trial", "extension"), rule("r2", "extension", "trial")]
        self.assertEqual(evaluate(doc)["obligations"]["item"]["status"], "unknown")
        self.assertEqual(evaluate(doc)["rounds"], 0)

    def test_no_implicit_exclusion_and_duplicate_ids_rejected(self):
        doc = contract()
        doc["facts"] = [fact("f1", "!trial"), fact("f2", "!extension")]
        self.assertEqual(evaluate(doc)["obligations"]["item"]["status"], "unknown")
        doc["rules"].append(rule("f1", "other", "trial"))
        with self.assertRaises(ValueError):
            evaluate(doc)
