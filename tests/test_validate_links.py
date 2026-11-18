import os
import sys
import requests
import pytest
from unittest.mock import patch, MagicMock

# Add scripts directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.validate_links import validate_url, MAX_RETRIES, RETRY_DELAY
from scripts import validate_links

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



def test_main_no_files(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(validate_links, "SOURCE_DIR", str(tmp_path))
    with patch("scripts.validate_links.validate_url") as check_url:
        with pytest.raises(SystemExit) as result:
            validate_links.main()
    assert result.value.code == 0
    check_url.assert_not_called()
    assert "No YAML files found to validate." in capsys.readouterr().out


def test_main_all_valid(tmp_path, monkeypatch, capsys):
    sidecar = tmp_path / "valid.yml"
    sidecar.write_text(
        "source_url: https://valid.example\ncitation:\n  doi: 10.1234/valid\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(validate_links, "SOURCE_DIR", str(tmp_path))
    with patch("scripts.validate_links.validate_url", return_value=None) as check_url:
        with pytest.raises(SystemExit) as result:
            validate_links.main()
    assert result.value.code == 0
    assert check_url.call_count == 2
    assert {call.args for call in check_url.call_args_list} == {
        ("https://valid.example", str(sidecar)),
        ("https://doi.org/10.1234/valid", str(sidecar)),
    }
    assert "✓ All links are valid." in capsys.readouterr().out


def test_main_broken_links(tmp_path, monkeypatch, capsys):
    sidecar = tmp_path / "broken.yml"
    sidecar.write_text("source_url: https://broken.example\n", encoding="utf-8")
    monkeypatch.setattr(validate_links, "SOURCE_DIR", str(tmp_path))
    broken = {"file": str(sidecar), "url": "https://broken.example", "status": 404, "type": "BROKEN"}
    with patch("scripts.validate_links.validate_url", return_value=broken) as check_url:
        with pytest.raises(SystemExit) as result:
            validate_links.main()
    assert result.value.code == 1
    check_url.assert_called_once_with("https://broken.example", str(sidecar))
    assert "Found 1 broken or invalid links:" in capsys.readouterr().out


def test_main_redirect_warning_links(tmp_path, monkeypatch, capsys):
    (tmp_path / "redirect.yml").write_text("source_url: https://redirect.example\n", encoding="utf-8")
    (tmp_path / "warning.yml").write_text("source_url: https://warning.example\n", encoding="utf-8")
    monkeypatch.setattr(validate_links, "SOURCE_DIR", str(tmp_path))

    def response(url, file_path):
        if url == "https://redirect.example":
            return {"file": file_path, "url": url, "status": 301,
                    "final_url": "https://final.example", "type": "REDIRECT"}
        return {"file": file_path, "url": url, "status": 403, "type": "WARNING"}

    with patch("scripts.validate_links.validate_url", side_effect=response) as check_url:
        with pytest.raises(SystemExit) as result:
            validate_links.main()
    assert result.value.code == 0
    assert check_url.call_count == 2
    output = capsys.readouterr().out
    assert "Found 1 redirected links" in output
    assert "Found 1 links with warnings" in output


def test_main_yaml_error(tmp_path, monkeypatch, capsys):
    (tmp_path / "malformed.yml").write_text("source_url: [\n", encoding="utf-8")
    monkeypatch.setattr(validate_links, "SOURCE_DIR", str(tmp_path))
    with patch("scripts.validate_links.validate_url") as check_url:
        with pytest.raises(SystemExit) as result:
            validate_links.main()
    assert result.value.code == 1
    check_url.assert_not_called()
    output = capsys.readouterr().out
    assert "ERROR: Could not read or parse YAML file." in output
    assert "Found 1 broken or invalid links:" in output
