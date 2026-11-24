import unittest
from scripts.ecoevo_pdf_grid import extract_native, extract_poppler, fingerprint
from tests.test_ecoevo_grid import tiny_grid_pdf

class VirtualGridTests(unittest.TestCase):
    def test_missing_inner_rules_use_header_and_closed_horizontal_bands(self):
        raw=tiny_grid_pdf(virtual=True)
        for result in (extract_native(raw),extract_poppler(raw)):
            with self.subTest(parser=result['parser']):
                self.assertEqual([r['item_id'] for r in result['rows']],['1.1','1.2','1.3'])
                self.assertEqual(result['rows'][0]['requirement_sha256'],fingerprint('Report outcomes. Include missing data.'))
                self.assertEqual(result['issues'],[])

    def test_three_line_header_and_items_inside_merged_group(self):
        raw=tiny_grid_pdf(virtual=True, merged=True)
        for result in (extract_native(raw),extract_poppler(raw)):
            with self.subTest(parser=result['parser']):
                self.assertEqual([r['item_id'] for r in result['rows']],['1.1','1.2','1.3'])
                self.assertEqual(result['rows'][0]['requirement_sha256'],fingerprint('Report outcomes. Include missing data.'))
                self.assertEqual(result['issues'],[])
