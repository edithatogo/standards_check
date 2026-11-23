import unittest
from unittest.mock import patch
from scripts.structured_source import html_structure, fingerprint


class HtmlTests(unittest.TestCase):
    def test_table_groups_spans_and_inline_block_text(self):
        raw = b'''<html><body><h2>Results</h2><table id="check"><caption>Checklist</caption>
        <thead><tr><th colspan="3">Heading</th></tr></thead><tbody>
        <tr><th rowspan="2" scope="rowgroup">Topic</th><td>1a</td><td>Meta<em>analysis</em><br>details</td></tr>
        <tr><td>1b</td><td><p>First.</p><ul><li>Second.</li></ul></td></tr>
        </tbody></table></body></html>'''
        text, report = html_structure(raw)
        table = report['blocks'][0]
        header, first, second = table['rows']
        self.assertEqual(header['group'], 'thead')
        self.assertEqual(header['cells'][0]['colspan'], 3)
        self.assertEqual(first['cells'][0]['rowspan'], 2)
        self.assertEqual(second['inherited_cells'], ['table/1/r2/c1'])
        self.assertIsNone(second['text_sha256'])
        self.assertEqual(second['cells'][0]['anchor'], 'table/1/r3/c2')
        self.assertEqual(first['cells'][1]['item_id_candidate'], '1a')
        self.assertEqual(first['cells'][2]['text_sha256'], fingerprint('Metaanalysis details'))
        self.assertEqual(second['cells'][1]['text_sha256'], fingerprint('First. Second.'))
        self.assertEqual(table['caption_sha256'], fingerprint('Checklist'))
        self.assertNotIn('Metaanalysis', str(report))
        self.assertIn('Metaanalysis', text)

    def test_direct_rows_and_implicit_rowspan_zero(self):
        text, report = html_structure(b'<table><tr><th rowspan="0">Topic</th><td>1</td></tr><tr><td>2</td></tr></table>')
        rows = report['blocks'][0]['rows']
        self.assertEqual(rows[1]['inherited_cells'], ['table/1/r1/c1'])
        self.assertEqual(rows[1]['cells'][0]['column'], 2)

    def test_incomplete_cell_never_gets_an_exact_fingerprint(self):
        text, report = html_structure(b'<table><tr><td>Literal<script>not a requirement</script><img src="external.png"></td></tr></table>')
        row = report['blocks'][0]['rows'][0]
        self.assertIsNone(row['text_sha256'])
        self.assertIsNone(row['cells'][0]['text_sha256'])
        self.assertIn('unsupported_cell_content', report['issues'])
        self.assertNotIn('not a requirement', text)

    def test_nested_tables_or_invalid_spans_are_not_silently_flattened(self):
        for raw in (b'<table><tr><td><table><tr><td>Nested</td></tr></table></td></tr></table>',
                    b'<table><tr><td rowspan="3">Too long</td></tr></table>',
                    b'<table><tr><td colspan="0">Invalid</td></tr></table>'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                html_structure(raw)
        with patch('scripts.structured_source.MAX_CELLS', 2), self.assertRaises(ValueError):
            html_structure(b'<table><tr><td colspan="3">Too wide</td></tr></table>')

if __name__ == '__main__':
    unittest.main()
