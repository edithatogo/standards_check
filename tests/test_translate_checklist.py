import unittest
from unittest.mock import MagicMock
from scripts.translate_checklist import translate_text

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

if __name__ == '__main__':
    unittest.main()
