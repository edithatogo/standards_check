"""E9 development-only comparison on fixed synthetic PDFs; no admission."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import platform
import re
import subprocess
import time
from collections import Counter
from importlib.metadata import version
from pathlib import Path

from .source_reconciliation import normalized

KINDS = ('row', 'nested', 'footnote', 'qualifier_link')
ITEM = re.compile(r'^(\d+(?:\.\d+){1,2})\s+(.+)$')
NOTE = re.compile(r'^\[([a-z])\]\s+(.+)$')
MARK = re.compile(r'\[([a-z])\]')
CONDITION = re.compile(r'^(?:If|Unless|When|Except when) [^,]+(?=,)')
Fact = tuple[str, int, str, str]
Observation = tuple[Fact, str]


def facts(pages: list[str]) -> list[Observation]:
    """Shared decoder; no reference input. Ambiguous score text is not erased."""
    out: list[Observation] = []
    for page, text in enumerate(pages, 1):
        rows: list[tuple[str, int, int, str]] = []
        notes: list[tuple[str, int, str]] = []
        scoring = False
        for line_no, line in enumerate(text.splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            if line.startswith('Sub-item number'):
                scoring = line.endswith('Score')
                continue
            if note := NOTE.fullmatch(line):
                notes.append((note[1], line_no, normalized(note[2])))
                continue
            if item := ITEM.fullmatch(line):
                value = item[2]
                if scoring:
                    value = re.sub(r'\s{2,}\d+(?:\.\d+)?$', '', value)
                rows.append((item[1], line_no, line_no, normalized(value)))
            elif rows and not notes:
                ident, start, _, value = rows[-1]
                rows[-1] = (ident, start, line_no, normalized(value + ' ' + line))
        ids = Counter(row[0] for row in rows)
        markers = Counter(note[0] for note in notes)
        for ident, start, end, value in rows:
            anchor = f'page/{page}/lines/{start}-{end}'
            out.append((('row', page, ident, value), anchor))
            parent = ident.rsplit('.', 1)[0]
            if ids[parent] == ids[ident] == 1:
                out.append((('nested', page, ident, parent), anchor))
            for marker in MARK.findall(value):
                if markers[marker] == 1:
                    out.append((('qualifier_link', page, ident, marker), anchor))
            if condition := CONDITION.match(value):
                out.append((('qualifier_link', page, ident, condition[0]), anchor))
        for ident, line_no, value in notes:
            out.append((('footnote', page, ident, value), f'page/{page}/lines/{line_no}-{line_no}'))
    return out


def score(gold: list[Fact], predicted: list[Observation]) -> dict:
    """Multiset exact match by kind, page, identity and content/edge."""
    reference = Counter(gold)
    observed = Counter(fact for fact, _ in predicted)
    result = {}
    for kind in KINDS:
        tp = sum(n for fact, n in (reference & observed).items() if fact[0] == kind)
        fp = sum(n for fact, n in (observed - reference).items() if fact[0] == kind)
        fn = sum(n for fact, n in (reference - observed).items() if fact[0] == kind)
        result[kind] = dict(tp=tp, fp=fp, fn=fn, precision=tp / (tp + fp) if tp + fp else None,
                            recall=tp / (tp + fn) if tp + fn else None)
    return result


def read_pages(raw: bytes, reader: str) -> list[str]:
    if reader == 'pdfplumber':
        import pdfplumber
        # Exact incumbent API used by scripts/extract_pdf_content.py.
        with pdfplumber.open(io.BytesIO(raw)) as pdf:
            return [page.extract_text() or '' for page in pdf.pages]
    if reader != 'poppler':
        raise ValueError('unsupported reader')
    # Same independent layout command as compare_prisma_source_pdf.py.
    data = subprocess.run(['pdftotext', '-layout', '-enc', 'UTF-8', '-', '-'],
                          input=raw, capture_output=True, check=True, timeout=15).stdout
    if len(data) > 100_000 or not data.endswith(b'\f'):
        raise ValueError('unexpected layout output')
    return data.decode('utf-8').removesuffix('\f').split('\f')


def run(reader: str, expected_version: str, revision: str) -> dict:
    import resource  # Linux-only experiment; ordinary tests do not require it.
    from tests.layout_fixture import REFERENCES, pages

    runtime = (version('pdfplumber') if reader == 'pdfplumber' else
               subprocess.run(['pdftotext', '-v'], capture_output=True, check=True, timeout=5)
               .stderr.decode().splitlines()[0].split()[-1])
    if runtime != expected_version:
        raise ValueError(f'unpinned reader version: {runtime}')
    started = time.perf_counter()
    cases = {}
    for case, raw in pages().items():
        annotations = REFERENCES[case]
        gold = [fact for fact, _ in annotations]
        observed_pages = read_pages(raw, reader)
        if len(observed_pages) != 1:
            raise ValueError('unexpected synthetic page count')
        predicted = facts(observed_pages)
        missing = Counter(gold) - Counter(fact for fact, _ in predicted)
        extra = Counter(fact for fact, _ in predicted) - Counter(gold)
        cases[case] = {'source_sha256': hashlib.sha256(raw).hexdigest(),
                       'reference': annotations, 'predictions': predicted,
                       'missing': list(missing.elements()), 'extra': list(extra.elements()),
                       'scores': score(gold, predicted), 'reader_pages': observed_pages}
    elapsed = time.perf_counter() - started
    totals = {}
    for kind in KINDS:
        tp, fp, fn = (sum(c['scores'][kind][key] for c in cases.values()) for key in ('tp', 'fp', 'fn'))
        totals[kind] = dict(tp=tp, fp=fp, fn=fn, precision=tp/(tp+fp) if tp+fp else None,
                            recall=tp/(tp+fn) if tp+fn else None)
    return {'experiment': 'E9-layout-development-v1', 'reader': reader, 'reader_version': runtime,
            'revision': revision, 'implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'python': platform.python_version(), 'platform': platform.platform(), 'model_weight_bytes': 0,
            'reference_status': 'author_labelled_synthetic_development', 'scientific_qualification': False,
            'canonical_packs_promoted': 0, 'seconds': elapsed,
            'peak_individual_process_rss_kib': max(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                                                   resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss),
            'scores': totals, 'cases': cases}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reader', choices=('pdfplumber', 'poppler'), required=True)
    parser.add_argument('--expected-version', required=True)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = run(args.reader, args.expected_version, args.revision)
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        result = {'experiment': 'E9-layout-development-v1', 'reader': args.reader,
                  'revision': args.revision, 'status': 'failed', 'error': str(exc),
                  'scientific_qualification': False, 'canonical_packs_promoted': 0}
        args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        raise SystemExit(1) from exc
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
