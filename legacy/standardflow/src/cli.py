import json

import click
from jsonschema import ValidationError

from .main import DIAGRAM_TYPES, SCHEMA_DIR, generate_artifact, validate_data


@click.group()
def cli():
    """Generate legacy research diagrams and checklists from JSON."""


@cli.command("list")
def list_types():
    """List diagram types and the supplied checklist fixtures."""
    click.echo("Available diagram types:")
    for name in DIAGRAM_TYPES:
        click.echo(f"- {name}")
    click.echo("\nAvailable checklist types:")
    for path in sorted((SCHEMA_DIR.parent / "data").glob("*checklist.json")):
        click.echo(f"- {path.stem.removesuffix('_checklist').upper()}")


@cli.command()
@click.argument("input", type=click.Path(exists=True, dir_okay=False))
@click.option("--output", "-o", default="output", help="Output file or checklist directory.")
@click.option("--style", "-s", type=click.Path(exists=True, dir_okay=False))
@click.option("--set", "set_values", multiple=True, help="Override a field with KEY=VALUE.")
def generate(input, output, style, set_values):
    """Generate an artifact from INPUT; diagrams default to PNG."""
    try:
        generate_artifact(input, output, style_path=style, set_values=set_values)
    except (OSError, ValueError, ValidationError) as error:
        raise click.ClickException(getattr(error, "message", str(error))) from error


@cli.command()
@click.argument("input", type=click.Path(exists=True, dir_okay=False))
def validate(input):
    """Validate INPUT; invalid data exits with a nonzero status."""
    try:
        with open(input, encoding="utf-8") as stream:
            validate_data(json.load(stream))
    except (OSError, ValueError, ValidationError) as error:
        raise click.ClickException(
            f"Validation failed: {getattr(error, 'message', str(error))}"
        ) from error
    click.echo("Validation successful!")


@cli.command()
@click.argument("name", required=False)
def schemas(name):
    """List canonical schemas or print one by name."""
    available = {
        path.name.removesuffix("_schema.json"): path
        for path in sorted(SCHEMA_DIR.glob("*_schema.json"))
    }
    if name is None:
        click.echo("Available schemas:")
        for key in available:
            click.echo(f"- {key.upper()}")
    elif name.lower() in available:
        click.echo(available[name.lower()].read_text(encoding="utf-8"))
    else:
        raise click.ClickException(f"Schema '{name}' not found.")


if __name__ == "__main__":
    cli()
