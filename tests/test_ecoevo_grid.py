import unittest
from scripts.ecoevo_pdf_grid import extract_native, extract_poppler, fingerprint, extract_grid, Word


def tiny_grid_pdf(virtual=False):
    pages=[]
    for page, rows in enumerate(([('1.1','Report outcomes.'),('1.2','Report harms.')],[('1.3','Report all data.')]),1):
        xs=(20,80,140,300,360)
        top=250; header_bottom=220; bottom=header_bottom-40*len(rows)
        cmds=['0.7 w']
        for x in (xs[0],xs[-1]) if virtual else xs: cmds.append(f'{x} {bottom} m {x} {top} l S')
        for y in (top,header_bottom,bottom): cmds.append(f'{xs[0]} {y} m {xs[-1]} {y} l S')
        for i in range(1,len(rows)): cmds.append(f'80 {header_bottom-40*i} m 360 {header_bottom-40*i} l S')
        def put(x,y,text): cmds.append(f'BT /F1 9 Tf {x} {y} Td ({text}) Tj ET')
        put(24,235,'Topic');put(84,238,'Sub-item');put(84,226,'number');put(144,235,'Sub-item');put(304,235,'Score')
        put(24,header_bottom-12,'Results')
        for i,(item,text) in enumerate(rows):
            y=header_bottom-12-40*i;put(84,y,item);put(144,y,text);put(304,y,'8.3')
            if item=='1.1': put(144,y-12,'Include missing data.')
        pages.append('\n'.join(cmds).encode())
    objs=[b'<< /Type /Catalog /Pages 2 0 R >>', b'<< /Type /Pages /Count 2 /Kids [4 0 R 6 0 R] >>',b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']
    for i,stream in enumerate(pages):
        objs.extend([f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 400 300] /Resources << /Font << /F1 3 0 R >> >> /Contents {5+2*i} 0 R >>'.encode(), f'<< /Length {len(stream)} >>\nstream\n'.encode()+stream+b'\nendstream'])
    data=bytearray(b'%PDF-1.4\n');offsets=[0]
    for i,obj in enumerate(objs,1):
        offsets.append(len(data));data.extend(f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n')
    start=len(data);data.extend(f'xref\n0 {len(offsets)}\n0000000000 65535 f \n'.encode())
    for offset in offsets[1:]: data.extend(f'{offset:010d} 00000 n \n'.encode())
    data.extend(f'trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode());return bytes(data)


class GridTests(unittest.TestCase):
    def test_multiline_header_merged_topic_and_closed_page_tails(self):
        raw=tiny_grid_pdf()
        for result in (extract_native(raw),extract_poppler(raw)):
            with self.subTest(parser=result['parser']):
                self.assertEqual([r['item_id'] for r in result['rows']],['1.1','1.2','1.3'])
                self.assertEqual(result['rows'][0]['requirement_sha256'],fingerprint('Report outcomes. Include missing data.'))
                self.assertEqual(result['rows'][1]['requirement_sha256'],fingerprint('Report harms.'))
                self.assertEqual(result['issues'],[])
                self.assertNotIn('Report outcomes',str(result))

    def test_unbound_continuation_cannot_qualify_prior_tail(self):
        words=[Word(2,2,8,6,'Sub-item'),Word(2,10,8,14,'number'),Word(12,2,18,6,'Sub-item'),Word(2,22,8,26,'1.1'),Word(12,22,18,26,'First.'),Word(12,42,18,46,'Continuation.')]
        rows,issues,_=extract_grid(words,[0,10,30],lambda a,b:[0,20,40,60],1)
        self.assertIsNone(rows[0]['requirement_sha256'])
        self.assertIn('unbound_requirement_band',issues)

    def test_header_absent_never_creates_rows(self):
        rows,issues,_=extract_grid([Word(2,2,8,6,'1.1'),Word(12,2,18,6,'Text')],[0,10,30],lambda a,b:[0,20],1)
        self.assertEqual(rows,[]); self.assertIn('header_not_unique',issues)

    def test_open_geometry_is_not_fingerprinted(self):
        words=[Word(2,2,8,6,'Sub-item'),Word(2,10,8,14,'number'),Word(12,2,18,6,'Sub-item'),Word(2,22,8,26,'1.1'),Word(12,22,18,26,'First.')]
        rows,issues,_=extract_grid(words,[0,10,30],lambda a,b:[0,20,40],1,lambda x,a,b:x!=30)
        self.assertIsNone(rows[0]['requirement_sha256']); self.assertIn('unclosed_row_geometry',issues)
