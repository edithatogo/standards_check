import os
import sys
from unittest.mock import MagicMock

# Add scripts directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.translate_checklist import translate_text

def test_translate_text_empty_input():
    """Test translate_text with empty or whitespace-only input."""
    model = MagicMock()
    tokenizer = MagicMock()

    assert translate_text([], model, tokenizer) == ""
    assert translate_text(["", "   ", "\n"], model, tokenizer) == ""

    # Assert model and tokenizer were not called
    model.generate.assert_not_called()
    tokenizer.assert_not_called()
    tokenizer.decode.assert_not_called()

def test_translate_text_valid_input():
    """Test translate_text with valid text input."""
    model = MagicMock()
    tokenizer = MagicMock()

    # Setup mocks
    mock_tokenized_inputs = {"input_ids": "mock_input_ids", "attention_mask": "mock_attention_mask"}
    tokenizer.return_value = mock_tokenized_inputs

    mock_translated_tokens = ["mock_tokens_1", "mock_tokens_2"]
    model.generate.return_value = mock_translated_tokens

    tokenizer.decode.side_effect = ["Translated string 1", "Translated string 2"]

    text = ["Hello world", "How are you?"]

    # Call function
    result = translate_text(text, model, tokenizer)

    # Assertions
    tokenizer.assert_called_once_with(text, return_tensors="pt", padding=True)
    model.generate.assert_called_once_with(**mock_tokenized_inputs)

    assert tokenizer.decode.call_count == 2
    # Verify exact arguments passed to decode
    assert tokenizer.decode.call_args_list[0][0][0] == "mock_tokens_1"
    assert tokenizer.decode.call_args_list[0][1] == {"skip_special_tokens": True}
    assert tokenizer.decode.call_args_list[1][0][0] == "mock_tokens_2"
    assert tokenizer.decode.call_args_list[1][1] == {"skip_special_tokens": True}

    assert result == ["Translated string 1", "Translated string 2"]
