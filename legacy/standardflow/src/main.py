import json
from pathlib import Path

from jsonschema import validate

from .checklist import Checklist
from .consort import ConsortDiagram
from .prisma import PrismaDiagram
from .strobe import StrobeDiagram

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"
DIAGRAM_TYPES = {
    "PRISMA": PrismaDiagram,
    "PRISMA_2020_UPDATED": PrismaDiagram,
    "CONSORT": ConsortDiagram,
    "CONSORT_CLUSTER": ConsortDiagram,
    "STROBE": StrobeDiagram,
    "STROBE_COHORT": StrobeDiagram,
}


def validate_data(data, schema_dir=None):
    """Validate one legacy diagram or checklist against the canonical schemas."""
    if not isinstance(data, dict) or sum(
        key in data for key in ("diagram_type", "checklist_type")
    ) != 1:
        raise ValueError("Provide exactly one of 'diagram_type' or 'checklist_type'.")

    if "diagram_type" in data:
        diagram_type = data["diagram_type"]
        if not isinstance(diagram_type, str) or diagram_type not in DIAGRAM_TYPES:
            raise ValueError(f"Unknown diagram type: {diagram_type}")
        schema_name = diagram_type.split("_", 1)[0].lower()
    else:
        schema_name = "checklist"

    schema_path = Path(schema_dir or SCHEMA_DIR) / f"{schema_name}_schema.json"
    with schema_path.open(encoding="utf-8") as stream:
        validate(instance=data, schema=json.load(stream))

    return data


def generate_artifact(
    input_path, output_path, style_path=None, set_values=None, schema_dir=None
):
    """Generate from a JSON file or an already parsed web submission."""
    if isinstance(input_path, dict):
        data = input_path.copy()
    else:
        with open(input_path, encoding="utf-8") as stream:
            data = json.load(stream)
    if not isinstance(data, dict):
        raise ValueError("The input JSON must be an object.")

    if style_path:
        with open(style_path, encoding="utf-8") as stream:
            data["style"] = json.load(stream)
    for item in set_values or ():
        key, separator, value = item.partition("=")
        if not key or not separator:
            raise ValueError("Overrides must use KEY=VALUE.")
        try:
            data[key] = json.loads(value)
        except json.JSONDecodeError:
            data[key] = value

    validate_data(data, schema_dir)
    if "diagram_type" in data:
        DIAGRAM_TYPES[data["diagram_type"]](data).generate(str(output_path))
    else:
        checklist = Checklist(data)
        output_path = Path(output_path)
        if output_path.suffix == ".md":
            output_path.write_text(checklist.to_markdown(), encoding="utf-8")
        elif not output_path.suffix:
            checklist.generate(str(output_path))
        else:
            raise ValueError("Use .md for a checklist file or no suffix for a directory.")


def main():
    """Keep the original `python -m src INPUT -o OUTPUT` entry point."""
    import sys

    from .cli import cli

    cli(["generate", *sys.argv[1:]])


if __name__ == "__main__":
    main()
