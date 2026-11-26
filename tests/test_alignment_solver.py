import itertools
import random
import unittest

from scripts.alignment_solver import solve


def oracle(edges, forbidden):
    feasible = []
    for mask in itertools.product((False, True), repeat=len(edges)):
        selected = [edge for edge, keep in zip(edges, mask, strict=True) if keep]
        components = {x: {x} for a, b, _ in edges for x in (a, b)}
        for a, b, _ in selected:
            merged = components[a] | components[b]
            for node in merged:
                components[node] = merged
        if any(b in components.get(a, {a}) for a, b in forbidden):
            continue
        feasible.append((sum(w for _, _, w in selected), sorted((min(a,b), max(a,b)) for a,b,_ in selected)))
    best = max(score for score, _ in feasible)
    winners = [pairs for score, pairs in feasible if score == best]
    return best, winners


class AlignmentSolverTests(unittest.TestCase):
    def test_transitive_incompatibility_and_ties(self):
        result = solve([("a", "b", 5), ("b", "c", 4), ("a", "c", 3)], [("a", "c")])
        self.assertEqual(result["status"], "candidate_optimum")
        self.assertEqual(result["selected"], [("a", "b")])
        self.assertEqual(result["score"], 5)
        result = solve([("a", "b", 5), ("b", "c", 5)], [("a", "c")])
        self.assertEqual(result["status"], "held_tie")
        self.assertEqual(result["selected"], [])

    def test_exact_generated_oracle(self):
        rng = random.Random(142)
        universe = list(itertools.combinations("abcde", 2))
        for _ in range(12):
            edges = [(a, b, rng.randint(1, 4)) for a, b in rng.sample(universe, 7)]
            forbidden = rng.sample(universe, 2)
            score, winners = oracle(edges, forbidden)
            result = solve(edges, forbidden)
            self.assertEqual(result["score"], score)
            if len(winners) == 1:
                self.assertEqual(result["status"], "candidate_optimum")
                self.assertEqual(result["selected"], winners[0])
            else:
                self.assertEqual(result["status"], "held_tie")
                self.assertEqual(result["selected"], [])

    def test_no_forced_matches_and_invalid_input(self):
        self.assertEqual(solve([("a", "b", 5)], [("a", "b")])["selected"], [])
        self.assertEqual(solve([], [])["score"], 0)
        for edges in ([('a', 'a', 1)], [('a', 'b', True)], [('a', 'b', 1), ('b','a', 2)]):
            with self.assertRaises(ValueError):
                solve(edges, [])
        self.assertEqual(solve([("a", str(i), 1) for i in range(21)], [])["status"], "held_limit")
