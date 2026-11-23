#!/usr/bin/env python3
"""Reconcile legacy checklist inventory with EQUATOR metadata; never certify content."""
from __future__ import annotations

import argparse
from collections import Counter
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]
PAGE = re.compile(r"^reporting-guidelines/([^/]+)/index\.qmd$")
YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
# Explicit, source-edition-scoped identifier fixtures; never used for text or rights approval.
IDENTIFIER_FIXTURES = {
    "arrive-2020": "arrive-2.0-2020", "cheers-2022": "cheers-2022",
    "coreq-2007": "coreq-2007", "prisma-p": "prisma-p-2015",
    "spirit-2025": "spirit-2025", "squire-2-0": "squire-2.0-2015",
    "srqr-2014": "srqr-2014",
}
GENERIC_TITLE_WORDS = {
    "prisma", "consort", "spirit", "strobe", "squire", "stard", "tripod",
    "arrive", "cheers", "coreq", "moose", "tidier", "conserve", "care",
    "the", "for", "and", "of", "reporting", "guidelines", "guideline",
    "checklist", "statement", "standards", "on", "a", "an",
}



def words(value: object) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", str(value or "").lower()))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def doi(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    raw = value.strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "doi:"):
        if raw.startswith(prefix):
            raw = raw[len(prefix):]
            break
    return raw if re.fullmatch(r"10\.\d{4,9}/\S+", raw) else None


def equator_slug(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    url = urlparse(value)
    if url.netloc.lower() not in ("equator-network.org", "www.equator-network.org"):
        return None
    m = re.fullmatch(r"/reporting-guidelines/([^/]+)/?", url.path)
    return m[1] if m else None


def validate_catalogue(catalogue: dict) -> list[dict]:
    if catalogue.get("rights_status") != "not_assessed_for_individual_guidelines":
        raise ValueError("EQUATOR metadata cannot assert checklist rights")
    rows = catalogue.get("guidelines")
    if not isinstance(rows, list) or not rows or catalogue.get("published_count") != len(rows):
        raise ValueError("EQUATOR source listing is incomplete")
    if not re.fullmatch(r"[0-9a-f]{40}", str(catalogue.get("source_revision", ""))):
        raise ValueError("unpinned EQUATOR source revision")
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("source_path"), str):
            raise ValueError("bad EQUATOR source row")
        match = PAGE.fullmatch(row["source_path"])
        if not match or match[1] == "under-development" or row.get("id") != "equator:" + match[1]:
            raise ValueError("EQUATOR row is not a published source identity")
        if row["id"] in seen:
            raise ValueError("duplicated EQUATOR row")
        seen.add(row["id"])
    return rows


def scan_local(root: Path, item: dict) -> tuple[list[dict], list[str], dict | None]:
    ident = item["id"]
    assets = []
    for level in ("archetypes", "variants"):
        folder = root / "source" / level
        for ext in (".pdf", ".docx", ".csv", ".html", ".txt"):
            path = folder / (ident + ext)
            if path.is_file() and not path.is_symlink():
                assets.append({"path": path.relative_to(root).as_posix(), "sha256": sha256(path)})
    views = []
    seen = set()
    task_text = None
    for level in ("archetypes", "variants"):
        for prefix in ("markdown/en", "markdown"):
            path = root / prefix / level / (ident + ".md")
            if path.is_file() and not path.is_symlink():
                relative = path.relative_to(root).as_posix()
                if relative not in seen:
                    views.append(relative)
                    seen.add(relative)
                if task_text is None:
                    task_text = re.findall(r"^\s*[-*] \[[ xX]\]\s*(.+)$", path.read_text(encoding="utf-8"), re.M)
    content = None
    if task_text is not None:
        task_text = [words(text) for text in task_text]
        content = {"item_count": len(task_text), "item_fingerprint": hashlib.sha256("\n".join(task_text).encode()).hexdigest() if task_text else None}
    return sorted(assets, key=lambda x:x["path"]), sorted(views), content



def scan_sidecar(root: Path, item: dict, assets: list[dict]) -> tuple[dict | None, list[str]]:
    paths = [root / "source" / level / (item["id"] + ".yml") for level in ("archetypes", "variants")]
    paths = [path for path in paths if path.is_file() and not path.is_symlink()]
    findings = []
    if len(paths) > 1:
        findings.append("multiple_legacy_sidecars")
    if not paths:
        return None, findings
    # Prefer the index's declared track, but never infer that its contents are true.
    preferred_dir = {"archetype": "archetypes", "variant": "variants"}.get(item.get("level"))
    path = next((p for p in paths if p.parent.name == preferred_dir), paths[0])
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return {"path": path.relative_to(root).as_posix(), "parse_status": "invalid"}, [*findings, "malformed_legacy_sidecar"]
    if not isinstance(data, dict):
        return {"path": path.relative_to(root).as_posix(), "parse_status": "invalid"}, [*findings, "malformed_legacy_sidecar"]
    recorded = str(data.get("checksum") or "").lower()
    claimed = str(item.get("checksum") or "").lower()
    actual = {a["sha256"] for a in assets}
    if recorded and actual and recorded not in actual:
        findings.append("legacy_checksum_disagrees_with_present_asset")
    if claimed and recorded and claimed != recorded:
        findings.append("index_sidecar_checksum_conflict")
    if claimed and actual and claimed not in actual:
        findings.append("index_checksum_disagrees_with_present_asset")
    normal = lambda x: re.sub(r"[^a-z0-9]", "", str(x or "").lower())
    if data.get("license") and item.get("license") and normal(data["license"]) != normal(item["license"]):
        findings.append("legacy_license_claim_conflict")
    if data.get("verified") is True:
        findings.append("legacy_sidecar_verified_not_evidence")
    return {
        "path": path.relative_to(root).as_posix(),
        "claimed_verified": data.get("verified") is True,
        "claimed_license": data.get("license"),
        "checksum_claim": data.get("checksum"),
        "source_url_claim": data.get("source_url"),
    }, findings


def suggest(item: dict, rows: list[dict]) -> tuple[dict | None, str, list[dict]]:
    lookup = {row["id"].split(":", 1)[1]: row for row in rows}
    exact_doi = doi(item.get("url"))
    slug = equator_slug(item.get("url"))
    basis = "unresolved"
    chosen = lookup.get(slug) if slug else None
    if chosen:
        basis = "equator_page_url"
    if not chosen and exact_doi:
        matches = [row for row in rows if doi(row.get("doi")) == exact_doi]
        if len(matches) == 1:
            chosen, basis = matches[0], "same_doi_candidate"
    if not chosen:
        ident = item["id"]
        for candidate, reason in ((ident, "same_slug_candidate"), (re.sub(r"-(?:19|20)\d{2}$", "", ident), "family_slug_candidate")):
            if candidate in lookup:
                chosen, basis = lookup[candidate], reason
                break
    if not chosen:
        acronym = words(item["id"].replace("-", " "))
        same = [row for row in rows if row.get("acronym") and words(row["acronym"]) == acronym]
        if len(same) == 1:
            # An acronym can denote unrelated extensions (PRISMA-A is
            # acupuncture, not PRISMA for Abstracts); require title support.
            signal = set(words(item.get("title")).split()) - GENERIC_TITLE_WORDS
            comparison = set(words(same[0].get("title")).split()) - GENERIC_TITLE_WORDS
            if signal and len(signal & comparison) * 2 >= len(signal):
                chosen, basis = same[0], "same_acronym_candidate"
    scored = []
    title = words(item.get("title"))
    if title:
        for row in rows:
            if isinstance(row.get("title"), str):
                score = round(SequenceMatcher(None, title, words(row["title"])).ratio(), 3)
                if score >= 0.72:
                    scored.append((score, row))
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    alternatives = [{"id": row["id"], "title_similarity": score} for score, row in scored[:3] if not chosen or row["id"] != chosen["id"]]
    if not chosen and scored:
        best = scored[0]
        if len(scored) == 1 or best[0] - scored[1][0] >= 0.08:
            chosen, basis = best[1], "title_similarity_suggestion"
    if not chosen:
        return None, "unresolved", alternatives
    return ({"id": chosen["id"], "page_url": chosen["page_url"],
             "source_blob_sha": chosen["source_blob_sha"], "title": chosen.get("title"),
             "acronym": chosen.get("acronym"), "doi": chosen.get("doi"),
             "metadata_status": chosen.get("metadata_status")}), basis, alternatives


def reconcile(root: Path, catalogue: dict) -> dict:
    rows = validate_catalogue(catalogue)
    index = yaml.safe_load((root / "source/index.yml").read_text(encoding="utf-8"))
    items = index.get("items") if isinstance(index, dict) else None
    if not isinstance(items, list) or not items:
        raise ValueError("missing legacy checklist inventory")
    ids = [item.get("id") for item in items]
    if any(not isinstance(x, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", x) for x in ids) or len(set(ids)) != len(ids):
        raise ValueError("duplicate or invalid legacy source ID")
    fixture_path = root / "tests/fixtures/held-guidelines/source-item-identities.json"
    fixtures = json.loads(fixture_path.read_text(encoding="utf-8")).get("editions", {}) if fixture_path.is_file() else {}
    found = []
    for item in items:
        candidate, basis, alternatives = suggest(item, rows)
        assets, views, content = scan_local(root, item)
        sidecar, sidecar_findings = scan_sidecar(root, item, assets)
        findings = ["legacy_content_not_authority", "rights_unassessed_for_legacy_text", *sidecar_findings]
        if not assets: findings.append("no_original_asset")
        if not views: findings.append("no_legacy_markdown")
        if item.get("variant_of") and item["variant_of"] not in ids:
            findings.append("orphan_variant_parent")
        if candidate and candidate["metadata_status"] == "needs_review":
            findings.append("equator_metadata_exception")
        version = str(item.get("version", ""))
        if candidate and YEAR.fullmatch(version):
            declared = {m.group() for key in ("title", "acronym") for m in YEAR.finditer(candidate.get(key) or "")}
            if declared and version not in declared:
                findings.append("possible_edition_difference")
        if candidate and basis in {"title_similarity_suggestion", "family_slug_candidate", "same_acronym_candidate"}:
            findings.append("identity_requires_source_confirmation")
        fixture = fixtures.get(IDENTIFIER_FIXTURES.get(item["id"], ""))
        identifier_count = len(fixture["item_ids"]) if fixture and isinstance(fixture.get("item_ids"), list) else None
        if identifier_count is not None and content and content["item_count"] != identifier_count:
            findings.append("legacy_count_differs_from_independent_identifier_fixture")
        canonical_count = None
        if item["id"] == "prisma-2020":
            pack_path = root / "packs/org.prisma/prisma/2020/pack.json"
            if pack_path.is_file():
                pack = json.loads(pack_path.read_text(encoding="utf-8"))
                canonical_count = len(pack["requirements"])
                if content and canonical_count != content["item_count"]:
                    findings.append("legacy_count_differs_from_canonical_pack")
        entry = {
            "legacy_id": item["id"], "legacy_title": item.get("title"), "legacy_status": item.get("status", "unset"),
            "legacy_version": version or None, "legacy_group": item.get("group"), "legacy_variant_of": item.get("variant_of"),
            "equator_candidate": candidate, "link_basis": basis, "alternatives": alternatives,
            "source_assets": assets, "legacy_sidecar": sidecar,
            "legacy_views": views, "legacy_item_inventory": content,
            "independent_identifier_count": identifier_count, "canonical_pack_item_count": canonical_count,
            "rights": "unassessed", "admission": "unverified_candidate" if candidate else "unresolved", "findings": sorted(findings),
        }
        found.append(entry)
    fingerprints = Counter(x["legacy_item_inventory"]["item_fingerprint"] for x in found
                           if x["legacy_item_inventory"] and x["legacy_item_inventory"]["item_fingerprint"])
    for x in found:
        desc = x["legacy_item_inventory"]
        if desc and fingerprints[desc["item_fingerprint"]] > 1:
            x["findings"].append("duplicate_legacy_item_text")
            x["findings"].sort()
    return {
        "schema_version": 1, "authority": "candidate_links_only_not_source_verification",
        "equator_revision": catalogue["source_revision"], "equator_published_count": len(rows),
        "legacy_item_count": len(found),
        "summary": {
            "by_link_basis": dict(sorted(Counter(row["link_basis"] for row in found).items())),
            "by_finding": dict(sorted(Counter(note for row in found for note in row["findings"]).items())),
            "with_original_assets": sum(bool(row["source_assets"]) for row in found),
            "with_legacy_markdown": sum(bool(row["legacy_views"]) for row in found),
            "verified_legacy_checklists": 0,
        },
        "legacy_items": found,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--catalogue", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = reconcile(args.root, json.loads(args.catalogue.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{report['legacy_item_count']} legacy records; proposed link bases: {report['summary']['by_link_basis']}; zero verified by this process")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
