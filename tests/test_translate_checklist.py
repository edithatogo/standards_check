import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from scripts.translate_checklist import translate_markdown_file, translate_text


def test_module_import_does_not_load_optional_model_dependencies():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; import scripts.translate_checklist; "
            "assert 'transformers' not in sys.modules; assert 'torch' not in sys.modules",
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_translate_markdown_file_preserves_structure_and_runs_translation(tmp_path):
    source = tmp_path / "checklist.md"
    source.write_text(
        "# Main Header\n"
        "---\n"
        "\n"
        "Normal text here\n"
        "  - List item 1\n"
        "    - Nested item\n",
        encoding="utf-8",
    )
    model = MagicMock()
    tokenizer = MagicMock()
    tokenized = {"input_ids": [[1], [2], [3]], "attention_mask": [[1], [1], [1]]}
    tokenizer.return_value = tokenized
    model.generate.return_value = [[11], [22], [33]]
    tokenizer.decode.side_effect = [
        "Texte normal ici",
        "- Élément de liste 1",
        "- Élément imbriqué",
    ]

    with patch(
        "scripts.translate_checklist._load_translation_model",
        return_value=(tokenizer, model),
    ) as load_model:
        result = translate_markdown_file(source, "fr")

    assert result == (
        "# Main Header\n"
        "---\n"
        "\n"
        "Texte normal ici\n"
        "  - Élément de liste 1\n"
        "    - Élément imbriqué\n"
    )
    load_model.assert_called_once_with("Helsinki-NLP/opus-mt-en-fr")
    tokenizer.assert_called_once_with(
        ["Normal text here", "- List item 1", "- Nested item"],
        return_tensors="pt",
        padding=True,
    )
    model.generate.assert_called_once_with(**tokenized)
    assert tokenizer.decode.call_args_list == [
        call([11], skip_special_tokens=True),
        call([22], skip_special_tokens=True),
        call([33], skip_special_tokens=True),
    ]


@pytest.mark.parametrize("content", ["", "# Title\n---\n\n", " \t\n\n"])
def test_non_translatable_markdown_does_not_load_a_model(tmp_path, content):
    source = tmp_path / "no-prose.md"
    source.write_text(content, encoding="utf-8")
    with patch("scripts.translate_checklist._load_translation_model") as load_model:
        assert translate_markdown_file(source, "fr") == content
    load_model.assert_not_called()


def test_translate_markdown_file_reports_missing_model(tmp_path, capsys):
    source = tmp_path / "checklist.md"
    source.write_text("Text to translate\n", encoding="utf-8")
    with patch(
        "scripts.translate_checklist._load_translation_model",
        side_effect=OSError("Model not found"),
    ) as load_model:
        with pytest.raises(SystemExit) as error:
            translate_markdown_file(source, "unknown-lang")
    assert error.value.code == 1
    load_model.assert_called_once_with("Helsinki-NLP/opus-mt-en-unknown-lang")
    assert "Model for target language 'unknown-lang' not found" in capsys.readouterr().out


class TestTranslateText(unittest.TestCase):
    """Retain the accepted #19 cases and the distinct assertions from #39."""

    def setUp(self):
        self.mock_model = MagicMock()
        self.mock_tokenizer = MagicMock()

    def assert_translation_not_called(self):
        self.mock_model.generate.assert_not_called()
        self.mock_tokenizer.assert_not_called()
        self.mock_tokenizer.decode.assert_not_called()

    def test_translate_text_empty_list(self):
        result = translate_text([], self.mock_model, self.mock_tokenizer)
        self.assertEqual(result, "")
        self.assert_translation_not_called()

    def test_translate_text_none(self):
        result = translate_text(None, self.mock_model, self.mock_tokenizer)
        self.assertEqual(result, "")
        self.assert_translation_not_called()

    def test_translate_text_whitespace_only(self):
        result = translate_text(["", "   ", "\t", "\n"], self.mock_model, self.mock_tokenizer)
        self.assertEqual(result, "")
        self.assert_translation_not_called()

    def test_translate_text_single_item(self):
        mock_tensors = {"input_ids": [123]}
        self.mock_tokenizer.return_value = mock_tensors
        self.mock_model.generate.return_value = [[456]]
        self.mock_tokenizer.decode.return_value = "bonjour"
        text = ["hello"]
        result = translate_text(text, self.mock_model, self.mock_tokenizer)
        self.assertEqual(result, ["bonjour"])
        self.mock_tokenizer.assert_called_once_with(text, return_tensors="pt", padding=True)
        self.mock_model.generate.assert_called_once_with(**mock_tensors)
        self.mock_tokenizer.decode.assert_called_once_with([456], skip_special_tokens=True)

    def test_translate_text_multiple_items(self):
        mock_tensors = {"input_ids": [123, 124], "attention_mask": [1, 1]}
        self.mock_tokenizer.return_value = mock_tensors
        self.mock_model.generate.return_value = [[456], [457]]
        self.mock_tokenizer.decode.side_effect = ["bonjour", "monde"]
        text = ["hello", "world"]
        result = translate_text(text, self.mock_model, self.mock_tokenizer)
        self.assertEqual(result, ["bonjour", "monde"])
        self.mock_tokenizer.assert_called_once_with(text, return_tensors="pt", padding=True)
        self.mock_model.generate.assert_called_once_with(**mock_tensors)
        self.assertEqual(
            self.mock_tokenizer.decode.call_args_list,
            [call([456], skip_special_tokens=True), call([457], skip_special_tokens=True)],
        )


if __name__ == "__main__":
    unittest.main()
