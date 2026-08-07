import os
import sys
import pytest
from unittest.mock import patch, MagicMock, mock_open

# Add scripts directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.translate_checklist import translate_text, translate_markdown_file

def test_translate_text_empty_input():
    """Test translate_text with empty or whitespace-only inputs."""
    mock_model = MagicMock()
    mock_tokenizer = MagicMock()

    assert translate_text([], mock_model, mock_tokenizer) == ""
    assert translate_text(None, mock_model, mock_tokenizer) == ""
    assert translate_text(["", "   ", "\t"], mock_model, mock_tokenizer) == ""

    # Ensure model and tokenizer were not called
    mock_model.generate.assert_not_called()
    mock_tokenizer.assert_not_called()

def test_translate_text_valid_input():
    """Test translate_text with valid strings."""
    mock_model = MagicMock()
    mock_tokenizer = MagicMock()

    # Setup mock tokenizer behavior
    # tokenizer() returns a dict with 'input_ids' etc., we don't strictly need to define what's inside
    # since model.generate takes **kwargs, but we can set it up to return something mockable.
    mock_tokenizer_output = {"input_ids": [1, 2]}
    mock_tokenizer.return_value = mock_tokenizer_output

    # Setup mock model.generate behavior
    mock_model.generate.return_value = [["translated_token_1"], ["translated_token_2"]]

    # Setup mock decode behavior
    mock_tokenizer.decode.side_effect = ["Translated 1", "Translated 2"]

    input_text = ["Hello", "World"]
    result = translate_text(input_text, mock_model, mock_tokenizer)

    assert result == ["Translated 1", "Translated 2"]

    # Verify tokenizer was called correctly
    mock_tokenizer.assert_called_once_with(input_text, return_tensors="pt", padding=True)

    # Verify model.generate was called correctly
    mock_model.generate.assert_called_once_with(**mock_tokenizer_output)

    # Verify decode was called for each token
    assert mock_tokenizer.decode.call_count == 2
    mock_tokenizer.decode.assert_any_call(["translated_token_1"], skip_special_tokens=True)
    mock_tokenizer.decode.assert_any_call(["translated_token_2"], skip_special_tokens=True)


@patch('scripts.translate_checklist.MarianMTModel.from_pretrained')
@patch('scripts.translate_checklist.MarianTokenizer.from_pretrained')
@patch('scripts.translate_checklist.translate_text')
def test_translate_markdown_file_success(mock_translate_text, mock_tokenizer_cls, mock_model_cls):
    """Test translating a valid markdown file."""
    # Mocking read lines
    mock_file_content = (
        "# Main Header\n"
        "---\n"
        "\n"
        "Normal text here\n"
        "  - List item 1\n"
        "    - Nested item\n"
    )

    # We want translate_text to just return mocked translations for the lines it's given
    # According to the logic, it translates non-empty lines that don't start with '#' and aren't '---'
    # Lines to translate: "Normal text here", "  - List item 1", "    - Nested item"
    # Stripped: "Normal text here", "- List item 1", "- Nested item"
    mock_translate_text.return_value = [
        "Texte normal ici",
        "- Élément de liste 1",
        "- Élément imbriqué"
    ]

    with patch('builtins.open', mock_open(read_data=mock_file_content)):
        result = translate_markdown_file("fake_path.md", "fr")

    expected_result = (
        "# Main Header\n"
        "---\n"
        "\n"
        "Texte normal ici\n"
        "  - Élément de liste 1\n"
        "    - Élément imbriqué\n"
    )

    assert result == expected_result

    # Ensure translate_text was called with the correct stripped lines
    mock_translate_text.assert_called_once()
    called_args = mock_translate_text.call_args[0]
    assert called_args[0] == [
        "Normal text here",
        "- List item 1",
        "- Nested item"
    ]

    # Verify HuggingFace classes were initialized
    mock_tokenizer_cls.assert_called_once_with("Helsinki-NLP/opus-mt-en-fr")
    mock_model_cls.assert_called_once_with("Helsinki-NLP/opus-mt-en-fr")


@patch('scripts.translate_checklist.MarianMTModel.from_pretrained')
@patch('scripts.translate_checklist.MarianTokenizer.from_pretrained')
def test_translate_markdown_file_model_not_found(mock_tokenizer_cls, mock_model_cls):
    """Test graceful exit when model is not found."""
    mock_tokenizer_cls.side_effect = OSError("Model not found")

    with pytest.raises(SystemExit) as exc_info:
        translate_markdown_file("fake_path.md", "unknown-lang")

    assert exc_info.value.code == 1
