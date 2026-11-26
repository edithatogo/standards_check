"""Join existing directory/source receipts; do not infer checklist qualification."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

MEMBERS = (
    "equator-catalogue.json",
    "equator-source-link-candidates.json",
    "equator-article-survey.json",
    "equator-legacy-alignment.json",
)


def index(rows):
    result = {row["id"]: row for row in rows}
    if len(result) != len(rows):
        raise ValueError("duplicate directory identity")
    return result


def coverage(catalogue, links, survey, legacy):
    revision = catalogue["source_revision"]
    if any(
        other != revision
        for other in (
            links["source_revision"],
            survey["source_revision"],
            legacy["equator_revision"],
        )
    ):
        raise ValueError("source revision mismatch")
    universe = index(catalogue["guidelines"])
    candidates = index(links["guidelines"])
    sources = index(survey["records"])
    if (
        not universe
        or set(universe) != set(candidates)
        or set(universe) != set(sources)
        or any(
            count != len(universe)
            for count in (
                catalogue["published_count"],
                links["published_count"],
                survey["summary"]["published_count"],
                legacy["equator_published_count"],
            )
        )
    ):
        raise ValueError("directory inventory mismatch")

    def verify_blob(key, blob):
        if key not in universe or universe[key]["source_blob_sha"] != blob:
            raise ValueError("directory blob mismatch")

    legacy_by_id = defaultdict(list)
    for item in legacy["legacy_items"]:
        candidate = item.get("equator_candidate")
        if candidate:
            key = candidate["id"]
            verify_blob(key, candidate["source_blob_sha"])
            legacy_by_id[key].append(item)
    bulk = defaultdict(list)
    for article in survey["bulk_articles"]:
        for key, blob in article["source_blobs"]:
            verify_blob(key, blob)
            bulk[key].append(article["status"])
    worklist = defaultdict(list)
    for article in survey["oa_source_worklist"]:
        for key in article["source_ids"]:
            if key not in universe:
                raise ValueError("worklist directory identity mismatch")
            worklist[key].append(article["status"])
    rows = []
    strata = defaultdict(list)
    for key, directory in sorted(universe.items()):
        link = candidates[key]
        source = sources[key]
        verify_blob(key, link["source_blob_sha"])
        verify_blob(key, source["source_blob_sha"])
        source_states = sorted(set(bulk[key]))
        if len(source_states) == 1:
            observation = source_states[0]
        elif source_states:
            observation = "multiple_bulk_observations"
        else:
            observation = "not_evidenced_in_bulk_receipt"
        row = {
            "id": key,
            "source_blob_sha": directory["source_blob_sha"],
            "metadata_status": directory["metadata_status"],
            "source_link_count": len(link["candidates"]),
            "article_survey_status": source["status"],
            "rights_observation": source.get("rights", "not_recorded"),
            "oa_worklist_statuses": sorted(set(worklist[key])),
            "source_observation": observation,
            "bulk_statuses": source_states,
            "legacy_candidates": sorted(item["legacy_id"] for item in legacy_by_id[key]),
            "legacy_original_candidate": any(item["source_assets"] for item in legacy_by_id[key]),
            "legacy_view_candidate": any(item["legacy_views"] for item in legacy_by_id[key]),
            "pipeline_evaluation": "not_evidenced_in_source_receipts",
        }
        rows.append(row)
        for kind in set(directory.get("study_types") or ["Unclassified"]):
            strata[kind].append(row)

    def summarize(group):
        return {
            "entries": len(group),
            "metadata_status": dict(Counter(row["metadata_status"] for row in group)),
            "survey_status": dict(Counter(row["article_survey_status"] for row in group)),
            "source_observation": dict(Counter(row["source_observation"] for row in group)),
            "rights_observation": dict(Counter(row["rights_observation"] for row in group)),
            "with_source_link_candidates": sum(row["source_link_count"] > 0 for row in group),
            "with_legacy_candidates": sum(bool(row["legacy_candidates"]) for row in group),
            "with_legacy_original_candidates": sum(
                row["legacy_original_candidate"] for row in group
            ),
        }

    summary = summarize(rows)
    summary.update(
        directory_entries=len(rows),
        legacy_records=len(legacy["legacy_items"]),
        bulk_article_status=dict(Counter(row["status"] for row in survey["bulk_articles"])),
        priority_article_status=dict(Counter(row["status"] for row in survey["priority_articles"])),
        end_to_end_qualified_from_these_receipts=0,
    )
    return {
        "schema_version": 1,
        "source_revision": revision,
        "boundary": "Source discovery and observation only; no inferred execution, rights or admission",
        "summary": summary,
        "study_type_strata": {kind: summarize(group) for kind, group in sorted(strata.items())},
        "rows": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--artifact", type=Path)
    inputs.add_argument("--directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    digest = None
    if args.artifact is not None:
        if args.artifact.stat().st_size > 16_000_000:
            raise ValueError("bounded source receipt archive required")
        digest = hashlib.sha256(args.artifact.read_bytes()).hexdigest()
        with zipfile.ZipFile(args.artifact) as archive:
            if any(archive.getinfo(name).file_size > 8_000_000 for name in MEMBERS):
                raise ValueError("bounded receipt member required")
            raw = [archive.read(name) for name in MEMBERS]
    else:
        paths = [args.directory / name for name in MEMBERS]
        if any(path.stat().st_size > 8_000_000 for path in paths):
            raise ValueError("bounded receipt member required")
        raw = [path.read_bytes() for path in paths]
    result = coverage(*(json.loads(data) for data in raw))
    result["archive_sha256"] = digest
    result["member_sha256"] = {
        name: hashlib.sha256(data).hexdigest() for name, data in zip(MEMBERS, raw, strict=True)
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
