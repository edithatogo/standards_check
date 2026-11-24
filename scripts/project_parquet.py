#!/usr/bin/env python3
"""Derived Parquet analytical snapshot; JSON/YAML remain the authority."""

from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import tempfile

import pyarrow as pa
import pyarrow.parquet as pq
import yaml

ROOT = Path(__file__).resolve().parents[1]
VERSION = "standardflow.analytics.v1"
TEXT_FIELDS = ("verbatim_text", "normalized_requirement", "guidance")
RIGHTS_FIELDS = ("status", "spdx", "license_url", "attribution", "redistribution")
STRINGS = pa.list_(pa.field("element", pa.string()))


def strings(names: str) -> list[tuple[str, pa.DataType]]:
    return [(name, pa.string()) for name in names.split()]


def schema(name: str, fields: list[tuple[str, pa.DataType]]) -> pa.Schema:
    return pa.schema(fields, metadata={b"projection": VERSION.encode(), b"table": name.encode()})


RIGHTS = strings("rights_status rights_spdx rights_license_url rights_attribution rights_redistribution")
PACK = strings("pack_id pack_version")
POSITION = [("ordinal", pa.int64())]
SCHEMAS = {
    "packs": schema("packs", PACK + strings(
        "kind title publisher source_url retrieved_at source_sha256 pack_json_sha256 "
        "verification_status verified_at source_manifest_claim_boundary"
    ) + RIGHTS + [("verified_by", STRINGS), ("verification_evidence", STRINGS),
                  ("requirement_count", pa.int64()), ("relationship_count", pa.int64()),
                  ("source_count", pa.int64())]),
    "requirements": schema("requirements", PACK + POSITION + strings(
        "requirement_id display_number section source_anchor pack_rights_status"
    ) + RIGHTS + [("rights_inherited", pa.bool_()), ("text_exported", pa.bool_()),
                  ("evidence_expectations", STRINGS)] +
        strings(" ".join(TEXT_FIELDS)) + strings(" ".join(f"{key}_sha256" for key in TEXT_FIELDS))),
    "relationships": schema("relationships", PACK + POSITION + strings("predicate target")),
    "sources": schema("sources", PACK + POSITION + strings(
        "source_id role url retrieved_at sha256 repository_path git_blob_sha1 local_legacy_path"
    ) + [("redistributed_in_pack", pa.bool_())]),
    "source_index": schema("source_index", POSITION + strings(
        "source_id title url version date declared_license publisher preferred_format "
        "level group variant_of status checksum"
    ) + [("canonical_admission", pa.bool_())]),
    "equator_guidelines": schema("equator_guidelines", POSITION + strings(
        "guideline_id page_url source_path source_blob_sha metadata_status "
        "source_repository source_revision rights_status"
    ) + [("canonical_admission", pa.bool_())]),
    "candidate_editions": schema("candidate_editions", POSITION + strings(
        "edition doi pmcid source_url source_sha256 licence_url attribution claim_boundary evidence"
    ) + [("row_count", pa.int64()), ("canonical_admission", pa.bool_())]),
    "candidate_rows": schema("candidate_rows", POSITION + strings(
        "edition item_id topic source_anchor source_sha256 text_sha256"
    ) + [("canonical_admission", pa.bool_())]),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def text_sha(value: str | None) -> str | None:
    return None if value is None else sha(value.encode("utf-8"))


def rights_fields(rights: dict) -> dict:
    return {f"rights_{key}": rights[key] for key in RIGHTS_FIELDS}


def unique(rows: list[dict], key: str) -> None:
    values = [row[key] for row in rows]
    if any(not isinstance(value, str) or not value for value in values):
        raise ValueError(f"invalid {key}")
    if len(set(values)) != len(values):
        raise ValueError(f"duplicate {key}")


def select(row: dict, fields: str) -> dict:
    return {key: row.get(key) for key in fields.split()}


def project(root: Path) -> tuple[dict[str, list[dict]], dict[str, str]]:
    """Derive rows and exact input-byte digests from a single read of each input."""
    root = root.resolve()
    tables: dict[str, list[dict]] = {name: [] for name in SCHEMAS}
    inputs: dict[str, str] = {}

    def load(path: Path):
        if path.is_symlink() or path.resolve() != path:
            raise ValueError(f"symlink input: {path}")
        data = path.read_bytes()
        inputs[path.relative_to(root).as_posix()] = sha(data)
        return yaml.safe_load(data) if path.suffix == ".yml" else json.loads(data)

    pack_paths = sorted((root / "packs").glob("**/pack.json"))
    if not pack_paths:
        raise ValueError("no canonical packs")
    for path in pack_paths:
        pack = load(path)
        if pack["schema_version"] != "dev.standardflow.standard-pack.v1":
            raise ValueError("unsupported pack schema")
        if path.parent.relative_to(root / "packs").as_posix() != pack["pack_id"]:
            raise ValueError("pack identity does not match directory")
        manifest = load(path.parent / "sources" / "manifest.json")
        if manifest["schema_version"] != "dev.standardflow.source-manifest.v1":
            raise ValueError("unsupported source manifest schema")
        requirements = pack["requirements"]
        relationships = pack.get("relationships", [])
        sources = manifest["sources"]
        unique(requirements, "id")
        unique(sources, "id")
        identity = {"pack_id": pack["pack_id"], "pack_version": pack["version"]}
        verification = pack["verification"]
        tables["packs"].append({
            **identity, **select(pack, "kind title"), **pack["authority"],
            **rights_fields(pack["rights"]),
            "pack_json_sha256": inputs[path.relative_to(root).as_posix()],
            "verification_status": verification["status"],
            "verified_at": verification["verified_at"],
            "verified_by": verification["verified_by"],
            "verification_evidence": verification["evidence"],
            "source_manifest_claim_boundary": manifest["claim_boundary"],
            "requirement_count": len(requirements), "relationship_count": len(relationships),
            "source_count": len(sources),
        })
        for ordinal, item in enumerate(requirements):
            inherited = item["rights"].get("inherit_from_pack") is True
            rights = pack["rights"] if inherited else item["rights"]
            # Do not use item-level clearance to bypass a more restrictive pack policy.
            allowed = rights["status"] == pack["rights"]["status"] == "cleared"
            tables["requirements"].append({
                **identity, "ordinal": ordinal, "requirement_id": item["id"],
                **select(item, "display_number section source_anchor evidence_expectations"),
                **rights_fields(rights), "rights_inherited": inherited,
                "pack_rights_status": pack["rights"]["status"], "text_exported": allowed,
                **{key: item[key] if allowed else None for key in TEXT_FIELDS},
                **{f"{key}_sha256": text_sha(item[key]) for key in TEXT_FIELDS},
            })
        for ordinal, item in enumerate(relationships):
            tables["relationships"].append({**identity, "ordinal": ordinal, **item})
        for ordinal, item in enumerate(sources):
            tables["sources"].append({
                **identity, "ordinal": ordinal, "source_id": item["id"],
                **select(item, "role url retrieved_at sha256 repository_path git_blob_sha1 "
                         "local_legacy_path redistributed_in_pack"),
            })
    unique(tables["packs"], "pack_id")

    index = load(root / "source/index.yml")["items"]
    unique(index, "id")
    for ordinal, item in enumerate(index):
        values = select(item, "title url version date publisher preferred_format level group "
                              "variant_of status checksum")
        # SafeLoader may resolve an unquoted ISO date. Preserve its ISO representation.
        if isinstance(values["date"], date):
            values["date"] = values["date"].isoformat()
        tables["source_index"].append({
            "ordinal": ordinal, "source_id": item["id"], **values,
            "declared_license": item.get("license"), "canonical_admission": False,
        })

    discovery = load(root / "source/equator/discovery.json")
    guidelines = discovery["guidelines"]
    if discovery["schema_version"] != 1 or discovery["published_count"] != len(guidelines):
        raise ValueError("unsupported discovery schema or count mismatch")
    unique(guidelines, "id")
    for ordinal, item in enumerate(guidelines):
        tables["equator_guidelines"].append({
            "ordinal": ordinal, "guideline_id": item["id"],
            **select(item, "page_url source_path source_blob_sha metadata_status"),
            **select(discovery, "source_repository source_revision rights_status"),
            "canonical_admission": False,
        })

    ledger = load(root / "source/official/authoritative-article-rows.json")
    if ledger["schema_version"] != 1:
        raise ValueError("unsupported article ledger schema")
    unique(ledger["editions"], "edition")
    for ordinal, edition in enumerate(ledger["editions"]):
        rows = edition["rows"]
        unique(rows, "item_id")
        tables["candidate_editions"].append({
            "ordinal": ordinal, **select(edition, "edition doi pmcid source_url source_sha256 "
                                                 "licence_url attribution"),
            **select(ledger, "claim_boundary evidence"),
            "row_count": len(rows), "canonical_admission": False,
        })
        for position, row in enumerate(rows):
            tables["candidate_rows"].append({
                "ordinal": position, "edition": edition["edition"],
                "source_sha256": edition["source_sha256"],
                **select(row, "item_id topic source_anchor"),
                "text_sha256": text_sha(row["text"]), "canonical_admission": False,
            })
    return tables, inputs


def check_files(output: Path, tables: dict[str, list[dict]], inputs: dict[str, str]) -> dict:
    """Read actual Parquet bytes, enforcing ordered row/value/schema conservation."""
    entries = {path.name: path for path in output.iterdir()}
    expected = {f"{name}.parquet" for name in SCHEMAS}
    if set(entries) not in (expected, expected | {"manifest.json"}):
        raise ValueError("projection file set mismatch")
    if any(path.is_symlink() or not path.is_file() for path in entries.values()):
        raise ValueError("projection must contain regular files only")
    receipt = {"schema_version": VERSION, "inputs": inputs, "tables": {}}
    for name, contract in SCHEMAS.items():
        path = entries[f"{name}.parquet"]
        table = pq.ParquetFile(path).read()
        if not table.schema.equals(contract, check_metadata=True):
            raise ValueError(f"{name}: schema mismatch")
        if table.to_pylist() != tables[name]:
            raise ValueError(f"{name}: ordered row conservation failed")
        receipt["tables"][name] = {"rows": table.num_rows, "sha256": sha(path.read_bytes())}
    return receipt


def verify_projections(root: Path, output: Path) -> dict:
    tables, inputs = project(root)
    actual = check_files(output, tables, inputs)
    path = output / "manifest.json"
    if not path.is_file() or json.loads(path.read_text(encoding="utf-8")) != actual:
        raise ValueError("projection manifest mismatch")
    return actual


def write_projections(root: Path, output: Path) -> dict:
    root, output = root.resolve(), output.resolve()
    if output == root or (output.is_relative_to(root) and
                          not output.is_relative_to(root / "target")):
        raise ValueError("write outside the repository or under target/")
    if output.exists():
        raise ValueError("output directory already exists")
    tables, inputs = project(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".parquet-", dir=output.parent) as temporary:
        stage = Path(temporary) / "snapshot"
        stage.mkdir()
        for name, contract in SCHEMAS.items():
            table = pa.Table.from_pylist(tables[name], schema=contract)
            pq.write_table(table, stage / f"{name}.parquet", compression="zstd",
                           version="2.6", use_compliant_nested_type=True)
        receipt = check_files(stage, tables, inputs)
        (stage / "manifest.json").write_text(
            json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8"
        )
        stage.rename(output)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true", help="verify an existing snapshot")
    args = parser.parse_args()
    action = verify_projections if args.check else write_projections
    receipt = action(args.root, args.output)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
