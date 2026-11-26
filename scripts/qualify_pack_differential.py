"""Synthetic cross-runtime pack validation across the shared pack-kind surface."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from copy import deepcopy
from pathlib import Path

from .qualify_legacy_prisma import run
from .validate_packs import validator

ROOT = Path(__file__).resolve().parents[1]
KINDS = (
    "reporting",
    "protocol",
    "conduct",
    "appraisal",
    "risk_of_bias",
    "regulatory",
    "metadata",
    "profile",
)


def cases(base):
    """Generate distinct pack kinds and fail-closed schema/identity mutations."""
    for kind in KINDS:
        pack = deepcopy(base)
        pack["pack_id"] = f"synthetic/{kind.replace('_', '-')}"
        pack["kind"] = kind
        pack["title"] = f"Synthetic {kind} validation"
        yield f"{kind}-valid", pack, True
        for defect in ("missing-title", "duplicate-item", "invalid-kind"):
            bad = deepcopy(pack)
            if defect == "missing-title":
                del bad["title"]
            elif defect == "duplicate-item":
                bad["requirements"].append(deepcopy(bad["requirements"][0]))
            else:
                bad["kind"] = "unknown-kind"
            yield f"{kind}-{defect}", bad, False


def accepts_python(pack, schema):
    if not schema.is_valid(pack):
        return False
    ids = [row["id"] for row in pack["requirements"]]
    return len(ids) == len(set(ids))


def qualify(cli: Path) -> dict:
    """Use actual Python schema and Rust CLI, not the historic legacy renderer."""
    fixture = ROOT / "contracts/examples/minimal-standard-pack.v1.json"
    raw = fixture.read_bytes()
    schema = validator("standard-pack.v1.schema.json")
    rows = []
    with tempfile.TemporaryDirectory(prefix=".pack-differential-", dir=ROOT) as temporary:
        for identifier, pack, expected in cases(json.loads(raw)):
            path = Path(temporary) / "pack.json"
            path.write_text(json.dumps(pack), encoding="utf-8")
            python_accepted = accepts_python(pack, schema)
            output = run([str(cli), "--json", "pack", "validate", str(path)], success=False)
            rust_accepted = output.returncode == 0
            row = {
                "id": identifier,
                "expected_acceptance": expected,
                "python_accepted": python_accepted,
                "rust_accepted": rust_accepted,
                "matched": python_accepted == rust_accepted == expected,
                "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            if rust_accepted:
                response = json.loads(output.stdout)
                row["matched"] &= response["ok"] is True
                row["matched"] &= response["result"]["requirements"] == len(pack["requirements"])
            else:
                error = json.loads(output.stderr)
                row["rust_error_kind"] = error["error"]["kind"]
                row["matched"] &= output.returncode == 1 and error["ok"] is False
            rows.append(row)
    return {
        "protocol": "synthetic-shared-pack-boundary-v1",
        "fixture_sha256": hashlib.sha256(raw).hexdigest(),
        "kinds": list(KINDS),
        "cases": rows,
        "qualified": all(row["matched"] for row in rows),
        "boundary": "Python schema and Rust pack ingress only; not legacy renderer parity.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rust-cli", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = qualify(args.rust_cli.resolve(strict=True))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if result["qualified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
