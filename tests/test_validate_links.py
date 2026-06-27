import os
import sys
import requests
from unittest.mock import patch, MagicMock

# Add scripts directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.validate_links import validate_url, MAX_RETRIES

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

    # Assert time.sleep was called MAX_RETRIES - 1 times
    assert mock_sleep.call_count == MAX_RETRIES - 1

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

    # Assert time.sleep was called 1 time
    assert mock_sleep.call_count == 1

    # Assert result is None (success)
    assert result is None
