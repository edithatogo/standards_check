import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


class TestExamples(unittest.TestCase):
    def test_canonical_notebook_cells_run_without_saved_outputs(self):
        root = Path(__file__).resolve().parent.parent
        with TemporaryDirectory() as directory:
            isolated = Path(directory)
            for name in ('src', 'schemas', 'data', 'examples/notebooks'):
                shutil.copytree(root / name, isolated / name,
                                ignore=shutil.ignore_patterns('__pycache__'))
            for notebook in sorted((isolated / 'examples/notebooks').glob('*.ipynb')):
                with self.subTest(notebook=notebook.name):
                    cells = json.loads(notebook.read_text())['cells']
                    code = '\n'.join(''.join(cell['source']) for cell in cells
                                     if cell['cell_type'] == 'code')
                    result = subprocess.run(
                        [sys.executable, '-c', code], cwd=notebook.parent,
                        capture_output=True, text=True, check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
            images = list((isolated / 'examples/images').glob('*.png'))
            self.assertEqual(len(images), 6)
            for image in images:
                self.assertTrue(image.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'))
