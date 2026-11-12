import sys
import os
import pytest
import yaml
import json

# Add scripts directory to path to import validate_schemas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))
from validate_schemas import validate_yaml_file

def test_import():
    assert callable(validate_yaml_file)

def test_validate_yaml_file_happy_path(tmp_path):
    schema_content = {
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        },
        "required": ["name"]
    }
    yaml_content = "name: 'Test Name'\n"

    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(schema_content))

    yaml_file = tmp_path / "test.yml"
    yaml_file.write_text(yaml_content)

    assert validate_yaml_file(str(yaml_file), str(schema_file)) is True

def test_validate_yaml_file_skip_template(tmp_path):
    schema_content = {
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        },
        "required": ["name"]
    }
    # This content represents a template because it contains '<kebab-case-id>'
    yaml_content = "id: <kebab-case-id>\nname: 'Template'\n"

    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(schema_content))

    yaml_file = tmp_path / "template.yml"
    yaml_file.write_text(yaml_content)

    # It should return True early and not fail validation
    assert validate_yaml_file(str(yaml_file), str(schema_file)) is True

def test_validate_yaml_file_not_found(tmp_path):
    schema_file = tmp_path / "schema.json"
    schema_file.write_text("{}")

    yaml_file = tmp_path / "missing.yml"

    # Should catch FileNotFoundError and return False
    assert validate_yaml_file(str(yaml_file), str(schema_file)) is False

def test_validate_yaml_file_schema_not_found(tmp_path):
    yaml_file = tmp_path / "test.yml"
    yaml_file.write_text("name: 'Test Name'\n")

    schema_file = tmp_path / "missing_schema.json"

    # Should catch FileNotFoundError and return False
    assert validate_yaml_file(str(yaml_file), str(schema_file)) is False

def test_validate_yaml_file_malformed_yaml(tmp_path):
    schema_content = {
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        }
    }
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(schema_content))

    # Invalid YAML (missing quote)
    yaml_content = "name: 'Test Name\n"
    yaml_file = tmp_path / "test.yml"
    yaml_file.write_text(yaml_content)

    # Should catch yaml.YAMLError and return False
    assert validate_yaml_file(str(yaml_file), str(schema_file)) is False

def test_validate_yaml_file_validation_error(tmp_path):
    schema_content = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name", "age"]
    }
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(schema_content))

    # Valid YAML but violates schema (age is not an integer)
    yaml_content = "name: 'Test Name'\nage: 'twenty'\n"
    yaml_file = tmp_path / "test.yml"
    yaml_file.write_text(yaml_content)

    # Should catch jsonschema.exceptions.ValidationError and return False
    assert validate_yaml_file(str(yaml_file), str(schema_file)) is False
