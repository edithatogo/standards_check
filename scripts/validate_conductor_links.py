"""Check plan/issue ownership offline, or reconcile it with read-only GitHub data."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections.abc import Iterator
from pathlib import Path
from typing import Any

REPOSITORY = "edithatogo/standards_check"
REGISTRY = "contracts/project/conductor-issues.v1.json"
CHECKBOX = re.compile(r"^\s*(?:>\s*)*(?:[-*+]|\d+[.)])\s+\[[\sxX]\]")
TASK = re.compile(r"^- \[([ xX])\] \*\*(T(\d{2})\.\d{3})\*\* \((.*?)\) (\S.*)$")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_json(path: Path) -> Any:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            require(key not in result, f"duplicate JSON field: {key}")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)


def marker(tracks: list[str]) -> str:
    return "<!-- standardflow:tracks=" + ",".join(tracks) + " -->"


def issue_link(number: int) -> str:
    return f"[#{number}](https://github.com/{REPOSITORY}/issues/{number})"


def plan_lines(text: str) -> Iterator[tuple[int, str]]:
    """Ignore fenced examples/comments; reject incomplete markup hiding work."""
    fence = ""
    comment = False
    for number, line in enumerate(text.splitlines(), 1):
        if fence:
            if re.fullmatch(
                r" {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*", line
            ):
                fence = ""
            continue
        if comment:
            end = line.find("-->")
            if end < 0:
                continue
            line, comment = line[end + 3 :], False
        while "<!--" in line:
            start = line.index("<!--")
            end = line.find("-->", start + 4)
            if end < 0:
                line, comment = line[:start], True
                break
            line = line[:start] + line[end + 3 :]
        opening = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if opening:
            fence = opening.group(1)
            continue
        yield number, line
    require(not fence and not comment, "unclosed plan code fence or comment")


def flatten_pages(payload: Any) -> list[dict[str, Any]]:
    require(isinstance(payload, list), "GitHub response must be a paginated array")
    rows = (
        [row for page in payload for row in page]
        if all(isinstance(p, list) for p in payload)
        else payload
    )
    require(all(isinstance(row, dict) for row in rows), "invalid GitHub response row")
    return rows


def github_pages(endpoint: str) -> list[dict[str, Any]]:
    # gh owns authentication and pagination; arguments are never evaluated by a shell.
    completed = subprocess.run(
        ["gh", "api", "--paginate", "--slurp", endpoint],
        capture_output=True,
        text=True,
        check=False,
        timeout=90,
    )
    require(completed.returncode == 0, "GitHub read failed; live reconciliation is unavailable")
    return flatten_pages(json.loads(completed.stdout))


def validate(
    root: Path,
    *,
    live: bool = False,
    github_issues: list[dict[str, Any]] | None = None,
    github_comments: dict[int, list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    root = root.resolve(strict=True)
    registry = read_json(root / REGISTRY)
    require(isinstance(registry, dict), "registry must be an object")
    require(
        set(registry) == {"schema_version", "repository", "tracks", "issues"},
        "unknown registry fields",
    )
    require(
        registry["schema_version"] == "dev.standardflow.conductor-issues.v1",
        "unsupported registry version",
    )
    require(registry["repository"] == REPOSITORY, "repository identity differs")
    require(
        isinstance(registry["tracks"], list) and registry["tracks"],
        "tracks must be a nonempty array",
    )
    tracks: dict[str, Path] = {}
    for track in registry["tracks"]:
        require(isinstance(track, dict) and set(track) == {"id", "plan"}, "invalid track fields")
        identifier, relative = track["id"], track["plan"]
        require(
            isinstance(identifier, str) and re.fullmatch(r"\d{2}", identifier) is not None,
            "invalid track ID",
        )
        require(identifier not in tracks, f"duplicate track: {identifier}")
        require(
            isinstance(relative, str)
            and re.fullmatch(rf"conductor/tracks/{identifier}-[a-z0-9-]+/plan\.md", relative)
            is not None,
            "invalid plan path",
        )
        path = root / relative
        require(
            not any(
                (root / Path(*Path(relative).parts[:i])).is_symlink()
                for i in range(1, len(Path(relative).parts) + 1)
            ),
            "symlinked plan path",
        )
        resolved = path.resolve(strict=True)
        require(
            resolved.is_relative_to(root) and resolved.is_file(),
            "plan escapes repository or is not a file",
        )
        tracks[identifier] = path
    actual_plans = set((root / "conductor/tracks").glob("*/plan.md"))
    require(set(tracks.values()) == actual_plans, "unregistered or missing Conductor plan")
    table_tracks = re.findall(
        r"(?m)^\| (\d{2}) \|", (root / "conductor/tracks.md").read_text(encoding="utf-8")
    )
    require(
        len(table_tracks) == len(set(table_tracks)) and set(table_tracks) == set(tracks),
        "track table and registry differ",
    )

    require(
        isinstance(registry["issues"], list) and registry["issues"],
        "issues must be a nonempty array",
    )
    bindings: dict[int, dict[str, Any]] = {}
    for issue in registry["issues"]:
        require(
            isinstance(issue, dict) and set(issue) == {"number", "tracks", "role", "reverse_link"},
            "invalid issue binding fields",
        )
        number, owned, role = issue["number"], issue["tracks"], issue["role"]
        require(
            type(number) is int and number > 0 and number not in bindings,
            "invalid or duplicate issue number",
        )
        require(
            isinstance(owned, list) and owned and all(isinstance(x, str) for x in owned),
            "invalid issue tracks",
        )
        require(
            owned == sorted(set(owned)) and set(owned) <= set(tracks),
            "unknown or duplicate issue track",
        )
        require(
            isinstance(role, str) and role in {"work", "historical", "bot"}, "unknown issue role"
        )
        reverse = issue["reverse_link"]
        require(isinstance(reverse, dict), "invalid reverse link")
        if role == "bot":
            require(
                set(reverse) == {"kind", "comment_id"} and reverse["kind"] == "comment",
                "bot reverse link must use a retained comment",
            )
            require(
                type(reverse["comment_id"]) is int and reverse["comment_id"] > 0,
                "invalid bot comment identity",
            )
        else:
            require(reverse == {"kind": "body"}, "issue reverse link must use its body")
        bindings[number] = issue

    tasks: dict[str, dict[str, Any]] = {}
    for track_id, path in tracks.items():
        for line_number, line in plan_lines(path.read_text(encoding="utf-8")):
            if not CHECKBOX.match(line):
                continue
            parsed = TASK.fullmatch(line)
            require(
                parsed is not None, f"unmapped plan item: {path.relative_to(root)}:{line_number}"
            )
            if parsed is None:
                raise ValueError("invalid task")
            state, task_id, prefix, owners_text, _ = parsed.groups()
            require(
                prefix == track_id and task_id not in tasks,
                f"wrong-track or duplicate task: {task_id}",
            )
            owners = [int(n) for n in re.findall(r"\[#(\d+)\]", owners_text)]
            require(bool(owners) and owners == sorted(set(owners)), f"invalid owners: {task_id}")
            require(
                owners_text == ", ".join(issue_link(n) for n in owners),
                f"invalid owner links: {task_id}",
            )
            require(
                all(n in bindings and track_id in bindings[n]["tracks"] for n in owners),
                f"unknown owner or track mismatch: {task_id}",
            )
            tasks[task_id] = {"track": track_id, "issues": owners, "complete": state.lower() == "x"}
    require(bool(tasks), "no registered plan items")
    used = {n for task in tasks.values() for n in task["issues"]}
    require(used == set(bindings), "issue has no owning plan item")
    for number, binding in bindings.items():
        actual_tracks = {task["track"] for task in tasks.values() if number in task["issues"]}
        require(
            actual_tracks == set(binding["tracks"]),
            f"issue tracks lack corresponding plan ownership: #{number}",
        )

    if live:
        require(
            github_issues is None and github_comments is None,
            "live and supplied evidence cannot be mixed",
        )
        github_issues = github_pages(
            f"repos/{REPOSITORY}/issues?state=all&sort=created&direction=asc&per_page=100"
        )
        github_comments = {
            n: github_pages(f"repos/{REPOSITORY}/issues/{n}/comments?per_page=100")
            for n, binding in bindings.items()
            if binding["role"] == "bot"
        }
    live_checked = github_issues is not None
    if github_issues is not None:
        observed: dict[int, dict[str, Any]] = {}
        for issue in github_issues:
            require(isinstance(issue, dict), "invalid live issue")
            if "pull_request" in issue:
                continue
            number = issue.get("number")
            if not isinstance(number, int) or isinstance(number, bool):
                raise ValueError("invalid live issue identity")
            require(
                number > 0 and number not in observed, "invalid or repeated live issue identity"
            )
            require(
                issue.get("html_url") == f"https://github.com/{REPOSITORY}/issues/{number}",
                "live issue repository differs",
            )
            require(issue.get("state") in {"open", "closed"}, "invalid live issue state")
            observed[number] = issue
        require(
            set(observed) == set(bindings),
            f"live issue coverage differs: unmapped={sorted(set(observed) - set(bindings))}, missing={sorted(set(bindings) - set(observed))}",
        )
        for number, binding in bindings.items():
            expected = marker(binding["tracks"])
            if binding["role"] == "bot":
                comments = (github_comments or {}).get(number, [])
                matched = [
                    c for c in comments if c.get("id") == binding["reverse_link"]["comment_id"]
                ]
                require(
                    len(matched) == 1
                    and re.findall(
                        r"<!-- standardflow:tracks=[^>]* -->", matched[0].get("body") or ""
                    )
                    == [expected],
                    f"missing or ambiguous bot reverse link: #{number}",
                )
            else:
                require(
                    re.findall(
                        r"<!-- standardflow:tracks=[^>]* -->", observed[number].get("body") or ""
                    )
                    == [expected],
                    f"missing or ambiguous issue reverse link: #{number}",
                )
        for task_id, task in tasks.items():
            require(
                task["complete"] or any(observed[n]["state"] == "open" for n in task["issues"]),
                f"unfinished task has no open owner: {task_id}",
            )
    return {
        "schema_version": "dev.standardflow.conductor-reconciliation.v1",
        "tracks": len(tracks),
        "plan_items": len(tasks),
        "issues": len(bindings),
        "plan_item_mapping_percent": 100,
        "issue_mapping_percent": 100,
        "live_github_checked": live_checked,
        "reverse_links_checked": live_checked,
        "coverage_universe": "All registered plan checkboxes; all non-PR repository issues when live checked.",
        "boundary": "Ownership and traceability only; task and issue states do not establish scientific acceptance.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--live",
        action="store_true",
        help="Read all issues and bot link comments using authenticated gh; no writes.",
    )
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.root, live=args.live), indent=2, sort_keys=True))
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
