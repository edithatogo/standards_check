#!/usr/bin/env python3
"""Validate recipes, PRISMA inputs and generated accessible artefacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, NoReturn

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError
from jsonschema.protocols import Validator

if __package__:
    from scripts.source_xml import parse_xml
else:
    from source_xml import parse_xml

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
RECIPES = ROOT / "recipes/prisma-2020"
INPUTS = ROOT / "contracts/examples/prisma-flow"
GENERATED = ROOT / "examples/generated/prisma-2020"

VARIANTS = {
    "new-databases-registers": (
        "new_databases_registers",
        "org.prisma/prisma-2020/new-databases-registers",
    ),
    "new-databases-registers-other-sources": (
        "new_databases_registers_other_sources",
        "org.prisma/prisma-2020/new-databases-registers-other-sources",
    ),
    "updated-databases-registers": (
        "updated_databases_registers",
        "org.prisma/prisma-2020/updated-databases-registers",
    ),
    "updated-databases-registers-other-sources": (
        "updated_databases_registers_other_sources",
        "org.prisma/prisma-2020/updated-databases-registers-other-sources",
    ),
}


def fail(message: str) -> NoReturn:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        fail(f"{path.relative_to(ROOT)} cannot be read as JSON: {error}")


def make_validator(name: str) -> Validator:
    path = SCHEMAS / name
    schema = load_json(path)
    if not isinstance(schema, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as error:
        fail(f"{path.relative_to(ROOT)} is not valid Draft 2020-12: {error.message}")
    return Draft202012Validator(schema, format_checker=FormatChecker())


def validate(path: Path, validator: Validator) -> dict[str, Any]:
    value = load_json(path)
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
    errors = sorted(
        validator.iter_errors(value),
        key=lambda error: "/".join(str(part) for part in error.absolute_path),
    )
    if errors:
        error = errors[0]
        pointer = "/".join(str(part) for part in error.absolute_path) or "<root>"
        fail(f"{path.relative_to(ROOT)} violates its schema at {pointer}: {error.message}")
    return value


def validate_svg(path: Path, scene: dict[str, Any]) -> None:
    try:
        root = parse_xml(path.read_bytes(), 16_000_000)
    except (OSError, ValueError) as error:
        fail(f"{path.relative_to(ROOT)} is not valid SVG XML: {error}")
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        fail(f"{path.relative_to(ROOT)} root element is not SVG")
    if root.attrib.get("role") != "img":
        fail(f"{path.relative_to(ROOT)} must expose role=img")
    if root.attrib.get("aria-labelledby") != "standardflow-title":
        fail(f"{path.relative_to(ROOT)} must identify its title")
    if root.attrib.get("aria-describedby") != "standardflow-description":
        fail(f"{path.relative_to(ROOT)} must identify its complete accessible description")
    namespace = {"svg": "http://www.w3.org/2000/svg"}
    for selector, identifier, expected in (
        ("svg:title", "standardflow-title", scene["title"]),
        ("svg:desc", "standardflow-description", scene["text_equivalent"]),
        ("svg:metadata", "standardflow-text-equivalent", scene["text_equivalent"]),
    ):
        element = root.find(selector, namespace)
        if element is None or not "".join(element.itertext()).strip():
            fail(f"{path.relative_to(ROOT)} is missing non-empty {selector}")
        if [candidate for candidate in root.iter() if candidate.get("id") == identifier] != [
            element
        ]:
            fail(f"{path.relative_to(ROOT)} {identifier} must resolve uniquely to {selector}")
        if "".join(element.itertext()) != expected:
            fail(f"{path.relative_to(ROOT)} {selector} differs from its scene")
    description = root.find("svg:desc", namespace)
    if description is None or "Flow relationships:" not in "".join(description.itertext()):
        fail(f"{path.relative_to(ROOT)} accessible description omits flow relationships")
    groups = root.findall(".//svg:g", namespace)
    if not any(group.attrib.get("role") == "list" for group in groups):
        fail(f"{path.relative_to(ROOT)} must expose the node collection as a list")
    nodes = [node for node in root.iter() if node.attrib.get("role") == "listitem"]
    if not nodes or any(not node.attrib.get("aria-label", "").strip() for node in nodes):
        fail(f"{path.relative_to(ROOT)} must expose labelled list-item nodes")
    if [node.attrib.get("id") for node in nodes] != [
        f"node-{node_id}" for node_id in scene["reading_order"]
    ]:
        fail(f"{path.relative_to(ROOT)} DOM reading order differs from its scene")
    expected_nodes = {f"node-{node['id']}": node for node in scene["nodes"]}
    for node in nodes:
        expected = expected_nodes.get(node.get("id"))
        if expected is None:
            fail(f"{path.relative_to(ROOT)} contains a node absent from its scene")
        # XML normalizes literal attribute whitespace before exposing the DOM.
        label = expected["aria_label"].replace("\r\n", "\n").translate({9: " ", 10: " ", 13: " "})
        if node.get("aria-label") != label:
            fail(f"{path.relative_to(ROOT)} accessible label differs from its scene")
        lines = ["".join(line.itertext()) for line in node.findall(".//svg:tspan", namespace)]
        if lines != expected["lines"]:
            fail(f"{path.relative_to(ROOT)} visible text differs from its scene")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-missing-generated", action="store_true")
    arguments = parser.parse_args()

    recipe_validator = make_validator("artifact-recipe.v1.schema.json")
    flow_validator = make_validator("prisma-flow.v1.schema.json")
    scene_validator = make_validator("scene-graph.v1.schema.json")

    if not (ROOT / "packs/org.prisma/prisma/2020/pack.json").is_file():
        fail("the PRISMA 2020 source Standard Pack is missing")

    for stem, (template, recipe_id) in VARIANTS.items():
        recipe_path = RECIPES / f"{stem}.json"
        input_path = INPUTS / f"{stem}.json"
        recipe = validate(recipe_path, recipe_validator)
        flow = validate(input_path, flow_validator)
        if recipe.get("recipe_id") != recipe_id:
            fail(f"{recipe_path.relative_to(ROOT)} has the wrong recipe_id")
        if recipe.get("source_standard") != "org.prisma/prisma/2020":
            fail(f"{recipe_path.relative_to(ROOT)} has the wrong source_standard")
        if recipe.get("input_contract") != "dev.standardflow.prisma-flow.v1":
            fail(f"{recipe_path.relative_to(ROOT)} has the wrong input contract")
        if flow.get("template") != template:
            fail(f"{input_path.relative_to(ROOT)} has the wrong template")
        serialized_recipe = json.dumps(recipe, ensure_ascii=False)
        if "{{" not in serialized_recipe or "}}" not in serialized_recipe:
            fail(f"{recipe_path.relative_to(ROOT)} contains no explicit bindings")

        svg_path = GENERATED / f"{stem}.svg"
        text_path = GENERATED / f"{stem}.txt"
        scene_path = GENERATED / f"{stem}.scene.json"
        expected = (svg_path, text_path, scene_path)
        missing = [path for path in expected if not path.is_file()]
        if missing and arguments.allow_missing_generated:
            continue
        if missing:
            fail(
                "missing generated artefacts: "
                + ", ".join(str(path.relative_to(ROOT)) for path in missing)
            )
        scene = validate(scene_path, scene_validator)
        if scene.get("recipe_id") != recipe_id:
            fail(f"{scene_path.relative_to(ROOT)} was generated by the wrong recipe")
        if scene.get("reading_order") != recipe.get("reading_order"):
            fail(f"{scene_path.relative_to(ROOT)} reading order differs from its recipe")
        if len(scene.get("nodes", [])) != len(recipe.get("nodes", [])):
            fail(f"{scene_path.relative_to(ROOT)} node count differs from its recipe")
        validate_svg(svg_path, scene)
        text = text_path.read_text(encoding="utf-8")
        if text != scene["text_equivalent"]:
            fail(f"{text_path.relative_to(ROOT)} text equivalent differs from its scene")

    print(f"Validated {len(VARIANTS)} PRISMA 2020 recipe/input families")


if __name__ == "__main__":
    main()
