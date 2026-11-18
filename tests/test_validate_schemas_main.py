import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_schemas import main



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
