import unittest
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


class TestTranslateText(unittest.TestCase):

    def setUp(self):
        self.mock_model = MagicMock()
        self.mock_tokenizer = MagicMock()

    def test_translate_text_empty_list(self):
        """Test with an empty list."""
        result = translate_text([], self.mock_model, self.mock_tokenizer)
        self.assertEqual(result, "")
        self.mock_model.generate.assert_not_called()
        self.mock_tokenizer.assert_not_called()

    def test_translate_text_none(self):
        """Test with None as input."""
        result = translate_text(None, self.mock_model, self.mock_tokenizer)
        self.assertEqual(result, "")
        self.mock_model.generate.assert_not_called()
        self.mock_tokenizer.assert_not_called()

    def test_translate_text_whitespace_only(self):
        """Test with a list containing only empty or whitespace strings."""
        result = translate_text(["", "   ", "\t", "\n"], self.mock_model, self.mock_tokenizer)
        self.assertEqual(result, "")
        self.mock_model.generate.assert_not_called()
        self.mock_tokenizer.assert_not_called()

    def test_translate_text_single_item(self):
        """Test with a single valid string."""
        # Setup mocks
        mock_tensors = {"input_ids": [123]}
        self.mock_tokenizer.return_value = mock_tensors
        self.mock_model.generate.return_value = [[456]]
        self.mock_tokenizer.decode.return_value = "bonjour"

        # Execute
        text = ["hello"]
        result = translate_text(text, self.mock_model, self.mock_tokenizer)

        # Assert
        self.assertEqual(result, ["bonjour"])
        self.mock_tokenizer.assert_called_once_with(text, return_tensors="pt", padding=True)
        self.mock_model.generate.assert_called_once_with(**mock_tensors)
        self.mock_tokenizer.decode.assert_called_once_with([456], skip_special_tokens=True)

    def test_translate_text_multiple_items(self):
        """Test with multiple valid strings."""
        # Setup mocks
        mock_tensors = {"input_ids": [123, 124]}
        self.mock_tokenizer.return_value = mock_tensors
        self.mock_model.generate.return_value = [[456], [457]]
        self.mock_tokenizer.decode.side_effect = ["bonjour", "monde"]

        # Execute
        text = ["hello", "world"]
        result = translate_text(text, self.mock_model, self.mock_tokenizer)

        # Assert
        self.assertEqual(result, ["bonjour", "monde"])
        self.mock_tokenizer.assert_called_once_with(text, return_tensors="pt", padding=True)
        self.mock_model.generate.assert_called_once_with(**mock_tensors)
        self.assertEqual(self.mock_tokenizer.decode.call_count, 2)
        self.mock_tokenizer.decode.assert_any_call([456], skip_special_tokens=True)
        self.mock_tokenizer.decode.assert_any_call([457], skip_special_tokens=True)


if __name__ == "__main__":
    unittest.main()
