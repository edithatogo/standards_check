import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import graph_development

from scripts.graph_development import edges, compare, load_fixture


class GraphDevelopmentTests(unittest.TestCase):
    def setUp(self):
        self.data = load_fixture()

    def test_edges_are_anchored_and_do_not_use_labels(self):
        first = edges(self.data)
        for query in self.data['queries']:
            query['relevant'] = []
        self.assertEqual(first, edges(self.data))
        self.assertEqual(len(first), 31)
        self.assertTrue(all(edge['anchor'] for edge in first))

    def test_dangling_reference_fails(self):
        self.data['targets'][0]['text'] += ' See Z9.'
        with self.assertRaises(ValueError):
            edges(self.data)

    def test_unknown_parent_fails(self):
        self.data['targets'][0]['heading'] = 'invalid'
        with self.assertRaises(ValueError):
            edges(self.data)

    def test_comparison_retains_denominator_and_paired_ids(self):
        result = compare(self.data)
        self.assertEqual(result['eligible_pairs'], 250)
        self.assertEqual(result['reference_associations'], 17)
        self.assertFalse(result['equivalence_inferred'])
        for method in result['methods'].values():
            self.assertEqual(len(method['paired']), 10)
            for row in method['paired']:
                self.assertEqual(len(row['lexical_scores']), 25)
                self.assertEqual(len(row['graph_scores']), 25)
                self.assertEqual(set(row['gained']), set(row['graph_hits']) - set(row['lexical_hits']))
                self.assertEqual(set(row['lost']), set(row['lexical_hits']) - set(row['graph_hits']))

    def test_invalid_reference_fails(self):
        self.data['queries'][0]['relevant'] = ['ZZ']
        with self.assertRaises(ValueError):
            compare(self.data)

    def test_fixture_pin_and_duplicate_ids(self):
        with patch.object(graph_development, 'FIXTURE_SHA256', 'bad'):
            with self.assertRaises(ValueError):
                load_fixture()
        self.data['targets'].append(self.data['targets'][0])
        with self.assertRaises(ValueError):
            edges(self.data)

    def test_duplicate_query_and_incumbent_mismatch(self):
        self.data['queries'].append(self.data['queries'][0])
        with self.assertRaises(ValueError):
            compare(self.data)
        self.data['queries'].pop()
        with patch.object(graph_development, 'lexical_rankings', return_value={}):
            with self.assertRaises(ValueError):
                compare(self.data)

    def test_cli_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'receipt.json'
            with patch('sys.argv', ['graph_development', '--output', str(output)]):
                graph_development.main()
            self.assertEqual(json.loads(output.read_text())['eligible_pairs'], 250)


if __name__ == '__main__':
    unittest.main()
