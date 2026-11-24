import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.compare_ecoevo_formats import (EXPECTED_IDS, fingerprint, collect_rows,
                                            compare_formats, pdf_tables, layout_ids, read_bounded, benchmark, COHORT)


def cell(text, col, anchor, value_type='s'):
    return {'text_sha256': fingerprint(text), 'column': col, 'anchor': anchor,
            'item_id_candidate': text, 'value_type': value_type}


def group(rows):
    return {'rows': [{'anchor': f'r{i}', 'cells': [cell(v, c, f'r{i}/c{c}')
             for c, v in enumerate(row, 1)]} for i, row in enumerate(rows, 1)]}


def tiny_pdf():
    # A real, small PDF table with a text layer; no extra fixture dependency.
    commands = ['0.5 w']
    for x in (40, 160, 280):
        commands.append(f'{x} 100 m {x} 160 l S')
    for y in (100, 130, 160):
        commands.append(f'40 {y} m 280 {y} l S')
    for x,y,value in ((45,140,'Sub-item number'), (165,140,'Sub-item'), (45,110,'1.1'), (165,110,'Example requirement.')):
        commands.append(f'BT /F1 10 Tf {x} {y} Td ({value}) Tj ET')
    stream = '\n'.join(commands).encode()
    objs = [b'<< /Type /Catalog /Pages 2 0 R >>', b'<< /Type /Pages /Count 1 /Kids [3 0 R] >>',
            b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 320 200] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
            b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
            f'<< /Length {len(stream)} >>\nstream\n'.encode() + stream + b'\nendstream']
    data = bytearray(b'%PDF-1.4\n')
    offsets = [0]
    for i, obj in enumerate(objs, 1):
        offsets.append(len(data)); data.extend(f'{i} 0 obj\n'.encode() + obj + b'\nendobj\n')
    start = len(data)
    data.extend(f'xref\n0 {len(offsets)}\n0000000000 65535 f \n'.encode())
    for offset in offsets[1:]:
        data.extend(f'{offset:010d} 00000 n \n'.encode())
    data.extend(f'trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode())
    return bytes(data)


class EcoEvoFormatTests(unittest.TestCase):
    def test_header_columns_not_numeric_scoring_columns_and_extra_ids(self):
        rows, issues = collect_rows(group([['Score','Sub-item number','Sub-item'],
                                         ['2.1','1.1','Alpha'], ['0.5','28.1','Extra']]))
        self.assertEqual([r['item_id'] for r in rows], ['1.1','28.1'])
        self.assertEqual(rows[0]['requirement_anchor'], 'r2/c3')
        self.assertEqual(issues, [])
        self.assertEqual(len(EXPECTED_IDS), 89)

    def test_pairwise_counts_duplicates_missing_and_difference(self):
        left, _ = collect_rows(group([['Sub-item number','Sub-item'],['1.1','Alpha'],['1.2','Beta'],['1.2','Duplicate'],['1.3','Gamma']]))
        right, _ = collect_rows(group([['Sub-item number','Sub-item'],['1.1','Alpha'],['1.2','Beta'],['1.3','Changed'],['1.4','New']]))
        result = compare_formats(left,right)
        self.assertEqual(result['compared'],2)
        self.assertEqual(result['exact_equal'],1)
        self.assertEqual(result['different_ids'],['1.3'])
        self.assertNotIn('Alpha',str(result))

    def test_formula_or_missing_cell_cannot_match(self):
        table = group([['Sub-item number','Sub-item'],['1.1','=1+1'],['1.2','']])
        table['rows'][1]['cells'][1]['value_type'] = 'f'
        rows,issues = collect_rows(table)
        self.assertEqual([r['requirement_sha256'] for r in rows],[None,None])
        self.assertIn('missing_or_ineligible_requirement',issues)

    def test_pdf_real_grid_and_layout_tokens(self):
        raw=tiny_pdf()
        receipt=pdf_tables(raw)
        rows,issues=collect_rows(receipt)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['item_id'],'1.1')
        self.assertEqual(rows[0]['requirement_sha256'],fingerprint('Example requirement.'))
        self.assertEqual(rows[0]['requirement_anchor'],'page/1/table/1/r2/c2')
        self.assertEqual(layout_ids('Topic   1.1    text 2.1\n\f   2.1   text'),
                         [{'item_id':'1.1','page':1,'line':1},{'item_id':'2.1','page':2,'line':1}])

    def test_receipt_comparison_is_bound_to_current_bytes_and_official_identity(self):
        csv, pdf, docx, xlsx = COHORT
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            official = root / 'official'; official.mkdir()
            probes = []
            for path, filename in COHORT.items():
                target = root / path; target.parent.mkdir(parents=True, exist_ok=True)
                raw = tiny_pdf() if path == pdf else b'candidate'
                target.write_bytes(raw)
                probe = {'path': path, 'source_sha256': hashlib.sha256(raw).hexdigest()}
                if path != pdf:
                    probe['source_structure'] = group([['Sub-item number','Sub-item'],['1.1','Example requirement.']])
                probes.append(probe)
                if path in (pdf, docx):
                    (official / filename).write_bytes(raw if path == pdf else b'different')
            (root / xlsx).write_bytes(b'changed')
            receipt = {'schema_version':3,'summary':{'verified_by_this_process':0},
                       'legacy_items':[{'legacy_id':'prisma-ecoevo','source_probes':probes}]}
            result = benchmark(receipt, root, official)
            by_path = {row['path']:row for row in result['sources']}
            self.assertEqual(by_path[pdf]['identity'],'official_bytes_equal')
            self.assertEqual(by_path[pdf]['expected_ids_recovered'],1)
            self.assertEqual(by_path[docx]['identity'],'official_bytes_different')
            self.assertEqual(by_path[xlsx]['identity'],'official_bytes_unavailable')
            self.assertEqual(by_path[xlsx]['expected_ids_recovered'],0)
            self.assertEqual(by_path[xlsx]['local_bytes'],'held_unavailable_or_changed')
            self.assertEqual(by_path[csv]['identity'],'local_derivative_no_official_csv')
            self.assertEqual(result['canonical_packs_promoted'],0)

    def test_bounded_read(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'source';p.write_bytes(b'abc')
            self.assertEqual(read_bounded(p,3),b'abc')
            with self.assertRaises(ValueError): read_bounded(p,2)

if __name__ == '__main__':
    unittest.main()
