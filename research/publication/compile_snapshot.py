"""Compile immutable exploratory publication snapshots from exact retained evidence.

This is an offline projection, not a scientific freeze or public release tool.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import zipfile
from pathlib import Path


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def lookup(data, path):
    for key in path.split('/') if path else ():
        data = data[int(key)] if isinstance(data, list) else data[key]
    return data


def select(data, selector):
    def walk(value, parts, names):
        if not parts:
            yield '/'.join(names) or selector or 'all', value
        elif parts[0] == '*':
            items = enumerate(value) if isinstance(value, list) else sorted(value.items())
            for key, child in items:
                yield from walk(child, parts[1:], [*names, str(key)])
        else:
            yield from walk(lookup(value, parts[0]), parts[1:], names)

    return walk(data, selector.split('/') if selector else [], [])


def write_exact(path, raw):
    try:
        with path.open('xb') as stream:
            stream.write(raw)
    except FileExistsError:
        if path.read_bytes() != raw:
            raise ValueError('immutable output collision') from None


def compile_snapshot(root, manifest, spec, output):
    inputs = list(csv.DictReader(manifest.read_text().splitlines(), delimiter='\t'))
    names = [r['file'] for r in inputs]
    if not names or len(set(names)) != len(names) or any(Path(n).name != n for n in names):
        raise ValueError('duplicate or unsafe input identity')
    inventory = {}
    for row in inputs:
        name = row['file']
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f'missing or unsafe input: {name}')
        raw = path.read_bytes()
        if digest(raw) != row['sha256']:
            raise ValueError(f'input digest mismatch: {name}')
        inventory[name] = raw
    parsed = {}
    metrics = []
    for panel in csv.DictReader(spec.read_text().splitlines(), delimiter='\t'):
        name, member = panel['file'], panel['member']
        key = (name, member)
        if key not in parsed:
            raw = inventory[name]
            if member:
                with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                    if archive.namelist().count(member) != 1 or archive.getinfo(member).file_size > 16_000_000:
                        raise ValueError('ambiguous or unbounded JSON member')
                    raw = archive.read(member)
            parsed[key] = json.loads(raw)
        matches = list(select(parsed[key], panel['selector']))
        if not matches:
            raise ValueError('empty projection')
        for arm, result in matches:
            denom = panel['denominator']
            if denom.startswith('@'):
                denom = lookup(result, denom[1:])
            for metric in panel['metrics'].split(';'):
                value = lookup(result, metric)
                if value is not None and (type(value) not in (int, float) or not math.isfinite(value)):
                    raise ValueError('non-numeric or nonfinite metric')
                metrics.append({'panel': panel['panel'], 'arm': arm, 'metric': metric,
                                'value': value, 'unit': panel['unit'], 'denominator': denom,
                                'reference': panel['reference'], 'file': name, 'member': member,
                                'selector': panel['selector']})
    keys = [(r['panel'], r['arm'], r['metric'], r['file'], r['member'], r['selector']) for r in metrics]
    if not metrics or len(set(keys)) != len(keys):
        raise ValueError('empty or duplicate metric identity')
    buf = io.StringIO(newline='')
    writer = csv.DictWriter(buf, fieldnames=list(metrics[0]), delimiter='\t', lineterminator='\n')
    writer.writeheader()
    writer.writerows(metrics)
    table = buf.getvalue().encode()
    provenance = {'schema_version': 1, 'compiler_sha256': digest(Path(__file__).read_bytes()),
                  'manifest_sha256': digest(manifest.read_bytes()), 'projection_sha256': digest(spec.read_bytes()),
                  'comparison_sha256': digest(table), 'inputs': inputs, 'metrics': len(metrics),
                  'boundary': 'Exploratory evidence only; no cross-panel pooling, admission or public release'}
    version = digest(json.dumps(provenance, sort_keys=True, separators=(',', ':')).encode())
    provenance['snapshot_sha256'] = version
    provenance_raw = (json.dumps(provenance, indent=2, allow_nan=False) + '\n').encode()
    directory = output / ('v1-' + version)
    directory.mkdir(parents=True, exist_ok=True)
    files = {'snapshot.json': provenance_raw, 'comparison.tsv': table,
             'inputs.tsv': manifest.read_bytes(), 'panels.tsv': spec.read_bytes(),
             'compile_snapshot.py': Path(__file__).read_bytes()}
    for name, raw in files.items():
        write_exact(directory / name, raw)
    # Preserve originals, including failed runs, without extracting or modifying them.
    # The bundle is an internal retention copy; do not publish it automatically.
    archive_bytes = io.BytesIO()
    with zipfile.ZipFile(archive_bytes, 'w', compression=zipfile.ZIP_STORED) as archive:
        for name, raw in sorted({**files, **{'raw/' + n: r for n, r in inventory.items()}}.items()):
            archive.writestr(zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0)), raw)
    write_exact(directory / 'evidence.zip', archive_bytes.getvalue())
    return directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--panels', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(compile_snapshot(args.inputs, args.manifest, args.panels, args.output))


if __name__ == '__main__':
    main()
