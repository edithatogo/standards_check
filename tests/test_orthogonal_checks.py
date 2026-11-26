import unittest

from scripts.orthogonal_checks import applicability, alignment, leakage, reachability, rewrite


class OrthogonalTests(unittest.TestCase):
    def test_leakage_detects_containment_across_fragments(self):
        result = leakage({"r1": "Amber quills drift past the quiet ridge"}, {"o1": ["new words AMBER quills", "drift past the quiet ridge extra"]}, n=5)
        self.assertEqual(result["status"], "held_match")
        self.assertEqual(result["matches"], [("r1", "o1", 3)])
        self.assertNotIn("quills", repr(result))

    def test_leakage_distinct_and_missing(self):
        self.assertEqual(leakage({"r": "one two three four five"}, {"o": ["six seven eight"]}, n=3)["status"], "clear_in_scope")
        self.assertEqual(leakage({}, {"o": ["test"]}, n=3)["status"], "held_incomplete")
        self.assertEqual(leakage({"r": "one two"}, {"o": ["one two"]}, n=3)["status"], "held_incomplete")
        self.assertEqual(leakage({"r": "one two three"}, {"o": []}, n=3)["status"], "held_incomplete")
        with self.assertRaises(ValueError):
            leakage({"r": "one two"}, {"o": ["one two"]}, n=0)

    def test_applicability_unknown_conflict_and_negative_witness(self):
        rules = {"cluster": ("trial", "clustered")}
        self.assertEqual(applicability(rules, {"trial": True})["cluster"], "unknown")
        self.assertEqual(applicability(rules, {"trial": True, "clustered": True})["cluster"], "required")
        self.assertEqual(applicability(rules, {"trial": False})["cluster"], "not_applicable")
        self.assertEqual(applicability(rules, {"trial": False, "clustered": "conflict"})["cluster"], "held_conflict")
        with self.assertRaises(ValueError):
            applicability(rules, {"trial": 1})

    def test_reachability_sound_deadlock_and_limit(self):
        net = {"move": ((1, 0), (0, 1))}
        good = reachability((1, 0), (0, 1), net)
        self.assertEqual(good["status"], "sound_in_scope")
        self.assertEqual(good["witness"], ["move"])
        bad = reachability((1, 0), (0, 1), {**net, "drop": ((1, 0), (0, 0))})
        self.assertEqual(bad["status"], "unsound")
        self.assertEqual(bad["deadlocks"], 1)
        self.assertEqual(reachability((1, 0), (0, 1), net, max_states=1)["status"], "held_limit")
        self.assertEqual(reachability((1, 0), (0, 1), {"grow": ((1, 0), (2, 0))}, max_tokens=2)["status"], "held_limit")
        with self.assertRaises(ValueError):
            reachability((1, 0), (0, 1), {"bad": ((-1, 0), (0, 1))})

    def test_alignment_global_transitivity_and_ties(self):
        edges = [("a", "b", 5), ("b", "c", 4), ("a", "c", 3)]
        result = alignment(edges, [("a", "c")])
        self.assertEqual(result["selected"], [("a", "b")])
        self.assertEqual(result["score"], 5)
        tie = alignment([("a", "b", 5), ("b", "c", 5)], [("a", "c")])
        self.assertEqual(tie["status"], "held_tie")
        self.assertEqual(tie["selected"], [])
        with self.assertRaises(ValueError):
            alignment([("a", "a", 1)], [])

    def test_span_rewrite_preserves_untouched_bytes(self):
        raw = b"% untouched\nDose: mg;  DOI: key.\n"
        result = rewrite(raw, [(18, 20, b"mg", b"milligram")])
        self.assertEqual(result, raw[:18] + b"milligram" + raw[20:])
        with self.assertRaises(ValueError):
            rewrite(raw, [(18, 20, b"kg", b"milligram")])
        with self.assertRaises(ValueError):
            rewrite(raw, [(18, 20, b"mg", b"x"), (19, 20, b"g", b"y")])

    def test_explicit_negative_and_limits(self):
        self.assertEqual(applicability({"r": ("!trial",)}, {"trial": False}), {"r": "required"})
        self.assertEqual(applicability({"r": ("!trial",)}, {}), {"r": "unknown"})
        self.assertEqual(leakage({"r": "x" * 1_000_001}, {"o": ["some words"]})["status"], "held_limit")
        self.assertEqual(leakage({"r": "ＡＭＢＥＲ quills drift"}, {"o": ["amber QUİLLS drift"]}, n=3)["status"], "clear_in_scope")
        self.assertEqual(leakage({"r": "ＡＭＢＥＲ quills drift"}, {"o": ["amber quills, drift"]}, n=3)["status"], "held_match")
        with self.assertRaises(ValueError):
            leakage({"source prose": "test"}, {"o": ["test"]})
        with self.assertRaises(ValueError):
            leakage({"r": "test"}, {"o": "test"})
        with self.assertRaises(ValueError):
            applicability({"r": ()}, {})
        with self.assertRaises(ValueError):
            reachability((1,), (0,), {}, max_tokens=0)
        self.assertEqual(reachability((2,), (0,), {}, max_tokens=1)["status"], "held_limit")
        self.assertEqual(reachability((1,), (2,), {})["status"], "unsound")
        self.assertEqual(alignment([("a", str(i), 1) for i in range(17)], [])["status"], "held_limit")
        with self.assertRaises(ValueError):
            alignment([("a", "b", 1), ("b", "a", 2)], [])
        with self.assertRaises(ValueError):
            rewrite(b"a", [(0, 1, b"a", b"b")] * 1001)
        self.assertEqual(rewrite(b"abc", []), b"abc")

    def test_net_parser(self):
        from scripts.orthogonal_checks import verify_pnml

        raw = b'''<pnml><net id="n" type="http://www.pnml.org/version-2009/grammar/pnmlcoremodel"><page id="p"><place id="a"><initialMarking><text>1</text></initialMarking></place><place id="b"/><transition id="t"/><arc id="i" source="a" target="t"/><arc id="o" source="t" target="b"/></page><finalmarkings><marking><place idref="b"><text>1</text></place></marking></finalmarkings></net></pnml>'''
        self.assertEqual(verify_pnml(raw)["status"], "sound_in_scope")
        for bad in (raw.replace(b'target="t"', b'target="b"'), raw.replace(b'<transition id="t"/>', b'<transition id="t"><guard/></transition>'), raw.replace(b'idref="b"', b'idref="x"'), raw.replace(b'<text>1</text>', b'<text>-1</text>'), raw.replace(b'<place id="b"/>', b'<place id="a"/>')):
            with self.assertRaises(ValueError):
                verify_pnml(bad)
