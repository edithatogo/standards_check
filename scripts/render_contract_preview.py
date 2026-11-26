"""Build a static, authored-contract-only preview; never export research data."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from html import escape
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
GRAPH = "contracts/analysis/requirement-graph.v0.1.0.json"
SCHEMA = "schemas/requirement-graph-plan.v1.schema.json"
FOLLOWUP = "contracts/publication/composition-graph.v0.1.0.json"
PROGRAMME = "contracts/publication/programme.v1.json"
SOURCES = {
    PROGRAMME: "programme.v1.json",
    FOLLOWUP: "composition-graph.v0.1.0.json",
    GRAPH: "requirement-graph.v0.1.0.json",
    SCHEMA: "requirement-graph-plan.v1.schema.json",
    "docs/research/publication-protocol.v0.1.0.md": "publication-protocol.v0.1.0.md",
    "docs/research/composition-graph-protocol.v0.1.0.md": "composition-graph-protocol.v0.1.0.md",
}


def registry(rows):
    ids = {row["id"] for row in rows}
    if len(ids) != len(rows):
        raise ValueError("duplicate registry identity")
    return ids


def require_planned(contract):
    if (
        contract["status"] != "planned"
        or contract["design"]["inputs"]
        or contract["freeze"] is not None
        or contract["runs"]
        or any(row["status"] != "planned" for row in contract["claims"])
    ):
        raise ValueError("preview permits only planned, input-free publication contracts")


def validate_graph(root, graph, schema, publication):
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(graph)
    registry(graph["sources"])
    inputs = registry(graph["existing_inputs"])
    tables = registry(graph["tables"])
    registry(graph["figures"])
    registry(graph["gates"])
    experiments = registry(publication["design"]["experiments"])
    if inputs & tables:
        raise ValueError("derived table shadows an existing input")
    for item in graph["existing_inputs"]:
        if not (root / item["producer"]).is_file():
            raise ValueError("missing existing input producer")
    all_tables = inputs | tables
    for item in graph["tables"]:
        if not set(item["experiment_ids"]) <= experiments:
            raise ValueError("unknown experiment")
        for ref in item["references"]:
            if (
                item["columns"].get(ref["column"]) not in {"str", "str?"}
                or ref["table"] not in all_tables
            ):
                raise ValueError("unbound table reference")
    for figure in graph["figures"]:
        if not set(figure["table_ids"]) <= all_tables:
            raise ValueError("unbound figure table")
    for gate in graph["gates"]:
        if not (root / gate["workflow"]).is_file():
            raise ValueError("missing workflow")
        plans = list((root / "conductor/tracks").glob(f"{gate['task'][1:3]}-*/plan.md"))
        if len(plans) != 1:
            raise ValueError("missing or ambiguous track")
        line = next(
            (line for line in plans[0].read_text().splitlines() if f"**{gate['task']}**" in line),
            "",
        )
        if f"[#{gate['issue']}]" not in line:
            raise ValueError("unbound gate task or issue")


def table(headers, rows):
    cells = "".join(f'<th scope="col">{escape(str(value))}</th>' for value in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{escape(str(value))}</td>" for value in row) + "</tr>"
        for row in rows
    )
    return (
        f"<div class='scroll'><table><thead><tr>{cells}</tr></thead>"
        f"<tbody>{body}</tbody></table></div>"
    )


def render(graph, publication, programme, revision):
    links = "".join(
        f'<li><a href="{escape(name)}">{escape(name)}</a></li>' for name in SOURCES.values()
    )
    experiments = table(
        ["Experiment", "Question", "Primary endpoint", "Decision rule"],
        [
            [
                row["id"],
                row["question"],
                row["primary_endpoint"]["name"],
                row["primary_endpoint"]["decision_rule"],
            ]
            for row in programme["design"]["experiments"] + publication["design"]["experiments"]
        ],
    )
    sources = table(
        ["Source", "Purpose", "Status"],
        [[row["id"], row["role"], "Release and rights not frozen"] for row in graph["sources"]],
    )
    outputs = table(
        ["Table", "Grain", "Experiments", "Columns", "Access"],
        [
            [
                row["id"],
                row["grain"],
                ", ".join(row["experiment_ids"]),
                ", ".join(f"{k}: {v}" for k, v in row["columns"].items()),
                row["access"],
            ]
            for row in graph["tables"]
        ],
    )
    figures = table(
        ["Figure", "Visualisation", "Source tables", "Purpose"],
        [
            [row["id"], row["visualization"], ", ".join(row["table_ids"]), row["purpose"]]
            for row in graph["figures"]
        ],
    )
    gates = table(
        ["Gate", "Conductor task", "Issue", "Workflow", "Acceptance"],
        [
            [row["id"], row["task"], row["issue"], row["workflow"], row["acceptance"]]
            for row in graph["gates"]
        ],
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>StandardFlow | Research contracts</title>
<style>body{{font:16px/1.55 system-ui,sans-serif;color:#182533;background:#f8fafc;margin:0}}main{{max-width:76rem;padding:2rem;margin:auto}}h1,h2{{color:#14334b}}a{{color:#145a88}}header{{border-bottom:3px solid #567b8a;padding-bottom:1rem}}code{{overflow-wrap:anywhere}}.scroll{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;background:white}}td,th{{padding:.65rem;vertical-align:top;text-align:left;border:1px solid #d3dde5;min-width:7rem}}th{{background:#e5edf2}}nav a{{margin-right:1rem}}section{{margin-top:2rem}}.status{{font-weight:bold}}@media(max-width:640px){{main{{padding:1rem}}}}</style></head>
<body><main><header><p>StandardFlow / Prospective research</p><h1>Reporting obligations, ontology coverage and editorial utility</h1><p class="status">Planned contracts only. Dataset release held. No empirical results or validated reporting gaps.</p><p>GitHub source revision: <code>{escape(revision)}</code></p><p><a href="https://github.com/edithatogo/standards_check">Authoritative repository</a> | <a href="manifest.json">File hashes</a></p></header>
<nav aria-label="Sections"><a href="#experiments">Experiments</a><a href="#sources">Sources</a><a href="#outputs">Tables</a><a href="#figures">Figures</a><a href="#gates">Gates</a><a href="#contracts">Contracts</a></nav>
<section id="experiments"><h2>Prospective experiments</h2>{experiments}</section>
<section id="sources"><h2>Ontology and bibliometric sources</h2>{sources}</section>
<section id="outputs"><h2>Planned analytical tables</h2>{outputs}</section>
<section id="figures"><h2>Planned figures</h2><p>Each figure will have a source table, labelled legend, text alternative and denominators. No illustrative scores are substituted for study results.</p>{figures}</section>
<section id="gates"><h2>Qualification gates</h2>{gates}</section>
<section id="contracts"><h2>Exact contract and protocol files</h2><ul>{links}</ul><p>Private preview only. No source text, vectors, manuscripts, reference labels, raw ontology or citation data.</p></section></main></body></html>\n"""


def build(root, output, revision):
    from .validate_publication_contract import validate

    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("exact source revision required")
    if output.exists() or output.is_symlink():
        raise ValueError("preview requires a new directory")
    root = root.resolve()
    payload = {}
    for path, name in SOURCES.items():
        source = root / path
        if not source.resolve().is_relative_to(root) or source.is_symlink():
            raise ValueError("unsafe source path")
        if source.stat().st_size > 1_000_000:
            raise ValueError("authored source exceeds preview size limit")
        payload[name] = source.read_bytes()
    graph, schema, publication, programme = (
        json.loads(payload[SOURCES[path]]) for path in (GRAPH, SCHEMA, FOLLOWUP, PROGRAMME)
    )
    for contract in (publication, programme):
        require_planned(contract)
        validate(contract, root)
        if contract["design"]["protocol"]["path"] not in SOURCES:
            raise ValueError("unlisted protocol")
    validate_graph(root, graph, schema, publication)
    payload["index.html"] = render(graph, publication, programme, revision).encode()
    payload["README.md"] = (
        b"---\ntitle: StandardFlow Research Contracts\nsdk: static\napp_file: index.html\n---\n\n"
        b"Private, contract-only research preview. Plans are not results; dataset release held.\n"
    )
    manifest = {
        "revision": revision,
        "publication_status": "planned",
        "dataset_status": "held",
        "files": {name: hashlib.sha256(raw).hexdigest() for name, raw in sorted(payload.items())},
    }
    output.mkdir(parents=True)
    for name, raw in payload.items():
        (output / name).write_bytes(raw)
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--revision", required=True)
    args = parser.parse_args()
    print(json.dumps(build(ROOT, args.output, args.revision), sort_keys=True))


if __name__ == "__main__":
    main()
