"""Offline E9 adapter, receipt and ambiguity controls (no model downloads)."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from importlib.metadata import version
from pathlib import Path
from unittest.mock import patch

from scripts import layout_development as layout
from tests.layout_fixture import pages
from tests.test_compare_ecoevo_formats import tiny_pdf


class LayoutReaderTests(unittest.TestCase):
    def test_incumbent_reads_identical_pinned_pdf_bytes_and_blank_page(self):
        raw = pages()['existing-grid']
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         'f0e1ed7adca73daf68a4a4c1794dc5b4fbd6af3d6b622fc1d876f0560e94a83c')
        self.assertEqual(layout.read_pages(raw, 'pdfplumber'),
                         ['Sub-item number Sub-item\n1.1 Example requirement.'])
        self.assertEqual(layout.read_pages(tiny_pdf(['0.5 w']), 'pdfplumber'), [''])

    def test_unknown_reader_and_malformed_poppler_output_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unsupported reader'):
            layout.read_pages(b'', 'unknown')
        for raw in (b'no page terminator', b'x' * 100_001 + b'\f'):
            with self.subTest(raw_size=len(raw)), patch.object(
                layout.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, raw)
            ), self.assertRaisesRegex(ValueError, 'unexpected layout output'):
                layout.read_pages(b'synthetic', 'poppler')

    @unittest.skipUnless(shutil.which('pdftotext'), 'Poppler not installed')
    def test_layout_reader_retains_qualifier_and_score_column_separation(self):
        result = layout.facts(layout.read_pages(pages()['nested-notes'], 'poppler'))
        self.assertIn(('row', 1, '1.1', 'Report outcomes. [a] Include missing data.'),
                      [fact for fact, _ in result])
        self.assertIn(('qualifier_link', 1, '1.1', 'a'), [fact for fact, _ in result])

    def test_ambiguous_notes_and_cross_page_markers_do_not_create_links(self):
        result = layout.facts(['\nUnbound preamble\n1.1 Report outcomes. [a]\n'
                               '[a] First note.\n[a] Conflicting note.\nUnbound tail.',
                               '1.1.1 Report timing. [a]'])
        self.assertEqual([fact for fact, _ in result if fact[0] == 'qualifier_link'], [])
        self.assertEqual([fact for fact, _ in result if fact[0] == 'nested'], [])
        self.assertEqual(len([fact for fact, _ in result if fact[0] == 'footnote']), 2)
        self.assertIn(('row', 1, '1.1', 'Report outcomes. [a]'), [fact for fact, _ in result])


@unittest.skipUnless(sys.platform.startswith('linux'), 'RSS receipt is Linux-specific')
class LayoutReceiptTests(unittest.TestCase):
    def test_actual_incumbent_receipt_conserves_inputs_and_failures(self):
        result = layout.run('pdfplumber', version('pdfplumber'), 'test-revision')
        self.assertEqual(result['revision'], 'test-revision')
        self.assertEqual(result['scores']['row'],
                         {'tp': 1, 'fp': 3, 'fn': 3, 'precision': .25, 'recall': .25})
        self.assertEqual(result['scores']['qualifier_link']['tp'], 2)
        self.assertEqual(result['cases']['nested-notes']['source_sha256'],
                         'd983ced46b3c3cec3196acbe2eabef04ae82e545abe8f25a6cd152a23e6e6173')
        self.assertEqual(len(result['cases']['nested-notes']['missing']), 3)
        self.assertEqual(len(result['cases']['nested-notes']['extra']), 3)
        self.assertFalse(result['scientific_qualification'])
        self.assertEqual(result['canonical_packs_promoted'], 0)
        self.assertEqual(result['model_weight_bytes'], 0)
        self.assertGreater(result['peak_individual_process_rss_kib'], 0)

    @unittest.skipUnless(shutil.which('pdftotext'), 'Poppler not installed')
    def test_actual_layout_receipt_has_identical_sources_and_full_row_recovery(self):
        runtime = subprocess.run(['pdftotext', '-v'], capture_output=True, check=True,
                                 timeout=5).stderr.decode().splitlines()[0].split()[-1]
        result = layout.run('poppler', runtime, 'test-revision')
        self.assertEqual(result['scores']['row'],
                         {'tp': 4, 'fp': 0, 'fn': 0, 'precision': 1.0, 'recall': 1.0})
        self.assertEqual(result['cases']['nested-notes']['missing'], [])
        self.assertEqual(result['cases']['nested-notes']['source_sha256'],
                         'd983ced46b3c3cec3196acbe2eabef04ae82e545abe8f25a6cd152a23e6e6173')

    def test_unpinned_version_and_wrong_page_count_fail_closed(self):
        with self.assertRaisesRegex(ValueError, 'unpinned reader version'):
            layout.run('pdfplumber', '0.0.0', 'test-revision')
        with patch.object(layout, 'read_pages', return_value=['one', 'two']):
            with self.assertRaisesRegex(ValueError, 'unexpected synthetic page count'):
                layout.run('pdfplumber', version('pdfplumber'), 'test-revision')

    def test_cli_retains_success_and_failed_receipts(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'receipt.json'
            args = ['layout_development', '--reader', 'pdfplumber', '--expected-version',
                    version('pdfplumber'), '--revision', 'test-revision', '--output', str(output)]
            with patch.object(sys, 'argv', args):
                layout.main()
            result = json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(result['scores']['row']['tp'], 1)
            args[4] = '0.0.0'
            with patch.object(sys, 'argv', args), self.assertRaises(SystemExit) as stopped:
                layout.main()
            self.assertEqual(stopped.exception.code, 1)
            result = json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(result['status'], 'failed')
            self.assertEqual(result['canonical_packs_promoted'], 0)
            self.assertFalse(result['scientific_qualification'])
            self.assertNotIn('scores', result)


if __name__ == '__main__':
    unittest.main()
