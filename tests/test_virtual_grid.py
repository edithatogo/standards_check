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

    def test_centered_number_and_requirement_lines_in_merged_group(self):
        from scripts.ecoevo_pdf_grid import Word, extract_virtual
        def w(x,y,text): return Word(x,y-4,x+min(35,4*len(text)),y+4,text)
        words=[w(20,5,'Sub'),w(20,15,'item'),w(20,25,'number'),w(70,15,'Sub-item'),w(230,15,'Reported'),
               w(20,44.5,'1.1'),w(70,39,'First'),w(70,50,'requirement.'),
               w(20,73,'1.2'),w(70,62,'Second'),w(70,73,'wrapped'),w(70,84,'requirement.')]
        rows,issues,_=extract_virtual(words,[10,280],lambda a,b:[0,30,100],1,lambda x,a,b:True)
        self.assertEqual(issues,[])
        self.assertEqual([r['requirement_sha256'] for r in rows],[fingerprint('First requirement.'),fingerprint('Second wrapped requirement.')])
