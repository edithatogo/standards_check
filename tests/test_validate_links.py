import os
import sys
import requests
from unittest.mock import patch, MagicMock

# Add scripts directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.validate_links import validate_url, MAX_RETRIES, RETRY_DELAY

@patch('scripts.validate_links.time.sleep')
@patch('scripts.validate_links.requests.head')
def test_validate_url_request_exception(mock_head, mock_sleep):
    """Test validate_url when requests.head raises a RequestException for all retries."""
    # Setup mock to raise an exception
    mock_head.side_effect = requests.RequestException("Connection error")

    url = "http://example.com"
    file_path = "test.yml"

    result = validate_url(url, file_path)

    # Assert requests.head was called MAX_RETRIES times
    assert mock_head.call_count == MAX_RETRIES
    mock_head.assert_called_with(url, allow_redirects=True, timeout=10)

    # Assert time.sleep was called MAX_RETRIES - 1 times with the correct delay
    assert mock_sleep.call_count == MAX_RETRIES - 1
    mock_sleep.assert_called_with(RETRY_DELAY)

    # Assert result is the expected error dictionary
    assert result is not None
    assert result['file'] == file_path
    assert result['url'] == url
    assert result['status'] == 'ERROR'
    assert result['error_message'] == 'Connection error'
    assert result['type'] == 'ERROR'

@patch('scripts.validate_links.time.sleep')
@patch('scripts.validate_links.requests.head')
def test_validate_url_success_after_retries(mock_head, mock_sleep):
    """Test validate_url when it fails initially but succeeds on a retry."""
    # Setup mock to raise an exception on first call, then succeed
    success_response = MagicMock()
    success_response.status_code = 200
    mock_head.side_effect = [requests.RequestException("Timeout"), success_response]

    url = "http://example.com"
    file_path = "test.yml"

    result = validate_url(url, file_path)

    # Assert requests.head was called 2 times
    assert mock_head.call_count == 2

    # Assert time.sleep was called 1 time with the correct delay
    assert mock_sleep.call_count == 1
    mock_sleep.assert_called_with(RETRY_DELAY)

    # Assert result is None (success)
    assert result is None

import yaml
from scripts.validate_links import main

@patch('scripts.validate_links.sys.exit')
@patch('scripts.validate_links.glob')
def test_main_no_files(mock_glob, mock_exit, capsys):
    """Test main when no YAML files are found."""
    mock_glob.return_value = []

    main()

    mock_exit.assert_any_call(0)
    captured = capsys.readouterr()
    assert "No YAML files found to validate." in captured.out

@patch('scripts.validate_links.sys.exit')
@patch('scripts.validate_links.validate_url')
@patch('scripts.validate_links.yaml.safe_load')
@patch('builtins.open')
@patch('scripts.validate_links.glob')
def test_main_all_valid(mock_glob, mock_open, mock_yaml_load, mock_validate_url, mock_exit, capsys):
    """Test main when all URLs are valid."""
    mock_glob.return_value = ['test.yml']

    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file

    # Return data that has both source_url and citation.doi
    mock_yaml_load.return_value = {
        'source_url': 'http://valid.com',
        'citation': {'doi': '10.1234/valid'}
    }

    # Validation returns None for valid links
    mock_validate_url.return_value = None

    main()

    mock_exit.assert_any_call(0)
    captured = capsys.readouterr()
    assert "✓ All links are valid." in captured.out

@patch('scripts.validate_links.sys.exit')
@patch('scripts.validate_links.validate_url')
@patch('scripts.validate_links.yaml.safe_load')
@patch('builtins.open')
@patch('scripts.validate_links.glob')
def test_main_broken_links(mock_glob, mock_open, mock_yaml_load, mock_validate_url, mock_exit, capsys):
    """Test main when broken URLs are encountered."""
    mock_glob.return_value = ['test.yml']

    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file

    mock_yaml_load.return_value = {
        'source_url': 'http://broken.com',
    }

    mock_validate_url.return_value = {
        "file": "test.yml", "url": "http://broken.com", "status": 404, "type": "BROKEN"
    }

    main()

    mock_exit.assert_any_call(1)
    captured = capsys.readouterr()
    assert "Found 1 broken or invalid links:" in captured.out

@patch('scripts.validate_links.sys.exit')
@patch('scripts.validate_links.validate_url')
@patch('scripts.validate_links.yaml.safe_load')
@patch('builtins.open')
@patch('scripts.validate_links.glob')
def test_main_redirect_warning_links(mock_glob, mock_open, mock_yaml_load, mock_validate_url, mock_exit, capsys):
    """Test main when redirected and warning URLs are encountered."""
    mock_glob.return_value = ['test1.yml', 'test2.yml']

    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file

    # Return different mock data for different files
    def yaml_load_side_effect(*args, **kwargs):
        if mock_yaml_load.call_count == 1:
            return {'source_url': 'http://redirect.com'}
        return {'source_url': 'http://warning.com'}
    mock_yaml_load.side_effect = yaml_load_side_effect

    def validate_url_side_effect(url, *args):
        if url == 'http://redirect.com':
            return {"file": "test1.yml", "url": url, "status": 301, "final_url": "http://final.com", "type": "REDIRECT"}
        return {"file": "test2.yml", "url": url, "status": 403, "type": "WARNING"}
    mock_validate_url.side_effect = validate_url_side_effect

    main()

    # Should exit with 0 if no BROKEN or ERROR links exist
    mock_exit.assert_any_call(0)
    captured = capsys.readouterr()
    assert "Found 1 redirected links" in captured.out
    assert "Found 1 links with warnings" in captured.out

@patch('scripts.validate_links.sys.exit')
@patch('scripts.validate_links.yaml.safe_load')
@patch('builtins.open')
@patch('scripts.validate_links.glob')
def test_main_yaml_error(mock_glob, mock_open, mock_yaml_load, mock_exit, capsys):
    """Test main when a YAML parsing error occurs."""
    mock_glob.return_value = ['test.yml']

    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file

    mock_yaml_load.side_effect = yaml.YAMLError("Parse error")

    main()

    mock_exit.assert_any_call(1)
    captured = capsys.readouterr()
    assert "ERROR: Could not parse YAML file." in captured.out
    assert "Found 1 broken or invalid links:" in captured.out
