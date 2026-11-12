import sys
import os
import pytest
import yaml
import json

# Add scripts directory to path to import validate_schemas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))
from validate_schemas import validate_yaml_file, main

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

# --- Tests for main() orchestration ---

def test_main_all_valid(mocker):
    # Mock glob to return a few dummy yaml files
    mocker.patch('validate_schemas.glob', return_value=['source/file1.yml', 'source/file2.yml'])

    # Mock validate_yaml_file to always return True (valid)
    mock_validate = mocker.patch('validate_schemas.validate_yaml_file', return_value=True)

    # Mock sys.exit to prevent the test from exiting and to check its call
    mock_exit = mocker.patch('sys.exit')

    main()

    # index.yml and 2 sidecars = 3 calls
    assert mock_validate.call_count == 3

    # Check that sys.exit was called with 0 (success)
    mock_exit.assert_called_once_with(0)

def test_main_index_invalid(mocker):
    mocker.patch('validate_schemas.glob', return_value=['source/file1.yml'])

    # Return False only for index.yml
    def mock_validate_impl(file_path, schema_path):
        if file_path == "source/index.yml":
            return False
        return True

    mock_validate = mocker.patch('validate_schemas.validate_yaml_file', side_effect=mock_validate_impl)
    mock_exit = mocker.patch('sys.exit')

    main()

    mock_exit.assert_called_once_with(1)

def test_main_sidecar_invalid(mocker):
    mocker.patch('validate_schemas.glob', return_value=['source/file1.yml', 'source/invalid_file.yml'])

    # Return False only for invalid_file.yml
    def mock_validate_impl(file_path, schema_path):
        if file_path == "source/invalid_file.yml":
            return False
        return True

    mock_validate = mocker.patch('validate_schemas.validate_yaml_file', side_effect=mock_validate_impl)
    mock_exit = mocker.patch('sys.exit')

    main()

    mock_exit.assert_called_once_with(1)

def test_main_skipped_files(mocker):
    # glob returns index.yml, _meta.template.yml, and a regular file
    mocker.patch('validate_schemas.glob', return_value=['source/index.yml', 'source/_meta.template.yml', 'source/regular.yml'])

    mock_validate = mocker.patch('validate_schemas.validate_yaml_file', return_value=True)
    mocker.patch('sys.exit')

    main()

    # Check calls. Should only be called for index file (first call) and regular.yml (second call)
    # Ensure it's not called with sidecar schema for index.yml or _meta.template.yml inside the loop
    from unittest.mock import call

    expected_calls = [
        call("source/index.yml", "schemas/index.schema.json"),
        call("source/regular.yml", "schemas/sidecar.schema.json")
    ]

    mock_validate.assert_has_calls(expected_calls, any_order=True)
    assert mock_validate.call_count == 2
