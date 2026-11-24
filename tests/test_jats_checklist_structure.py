"""Independent synthetic structural controls; no guideline text is reproduced."""
import unittest
from xml.etree import ElementTree as ET

from scripts.jats_checklist_structure import describe_table


def structure(body: str, anchors: tuple[str, ...] = ()) -> dict:
    wrapper = ET.fromstring('<table-wrap id="T"><table><tbody>' + body + '</tbody></table>'
                            '<table-wrap-foot><fn id="f1"><p>Example note.</p></fn></table-wrap-foot>'
                            '</table-wrap>')
    return describe_table(wrapper, [{"source_anchor": anchor} for anchor in anchors])


class JatsStructureTests(unittest.TestCase):
    def test_spans_sections_and_nested_requirements(self):
        result = structure(
            '<tr><td colspan="3">Methods</td></tr>'
            '<tr><td rowspan="2">Topic</td><td>1a</td><td><p>First.</p>'
            '<list><list-item><p>Second.</p></list-item></list>'
            '<xref ref-type="table-fn" rid="f1">a</xref></td></tr>'
            '<tr><td>1b</td><td>meta<italic>analysis</italic></td></tr>',
            ('T:row:2:item:1a', 'T:row:3:item:1b'))
        first, second, third = result['rows']
        self.assertEqual(first['cells'][0]['colspan'], 3)
        self.assertEqual(second['source_anchor'], 'T:row:2:item:1a')
        self.assertEqual(second['section_row'], 1)
        self.assertEqual(third['inherited_cells'], ['T:row:2:cell:1'])
        self.assertEqual(third['cells'][0]['column'], 2)
        self.assertEqual(second['cells'][2]['block_boundary_loss'], True)
        self.assertFalse(third['cells'][1]['block_boundary_loss'])
        self.assertEqual([b['tag'] for b in second['cells'][2]['blocks']], ['p', 'list-item', 'p'])
        self.assertEqual(second['cells'][2]['footnote_refs'], ['f1'])
        self.assertEqual(result['footnotes'][0]['id'], 'f1')
        self.assertNotIn('Example note.', str(result))
        self.assertIn('block_boundary_difference', result['issues'])
        self.assertEqual(result['status'], 'held_structural_discrepancy')

    def test_unclassified_row_and_missing_footnote_are_not_ignored(self):
        result = structure('<tr><td>Unnumbered</td><td>Requirement.</td></tr>'
                           '<tr><td>1</td><td>Text <xref ref-type="fn" rid="missing">b</xref></td></tr>',
                           ('T:row:2:item:1',))
        self.assertEqual(result['rows'][0]['role'], 'unclassified')
        self.assertIn('unclassified_row', result['issues'])
        self.assertIn('unresolved_footnote_reference', result['issues'])
        self.assertEqual(result['status'], 'held_structural_discrepancy')

    def test_simple_numbered_row_is_observed_not_certified(self):
        result = structure('<tr><td>1</td><td>Report.</td></tr>', ('T:row:1:item:1',))
        self.assertEqual(result['issues'], [])
        self.assertEqual(result['status'], 'structure_observed_not_qualified')
        self.assertEqual(result['rows'][0]['cells'][1]['column'], 2)

    def test_unsupported_or_invalid_layouts_fail_closed(self):
        for body in ('<tr><td rowspan="99">A</td></tr>',
                     '<tr><td colspan="0">A</td></tr>',
                     '<tr><td><table><tbody><tr><td>A</td></tr></tbody></table></td></tr>',
                     '<tr><td>A</td><td rowspan="2">B</td></tr><tr><td colspan="2">C</td></tr>'):
            with self.subTest(body=body), self.assertRaises(ValueError):
                structure(body)

    def test_missing_or_duplicate_numbered_anchor_rejected(self):
        for anchors in (('T:row:9:item:1',), ('T:row:1:item:1', 'T:row:1:item:2')):
            with self.subTest(anchors=anchors), self.assertRaises(ValueError):
                structure('<tr><td>1</td><td>Report.</td></tr>', anchors)


if __name__ == '__main__':
    unittest.main()
