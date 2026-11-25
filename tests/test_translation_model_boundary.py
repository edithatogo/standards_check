"""An opt-in model load needs an immutable revision and cannot lose source rows."""

from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from scripts import translate_checklist as translation

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "revision", [None, "", "main", "v1.0", "a" * 39, "a" * 41, "A" * 40, "g" * 40]
)
def test_unpinned_revision_is_rejected_before_importing_optional_dependencies(revision):
    with patch.dict(sys.modules, {"transformers": None}):
        with pytest.raises(ValueError, match="exact 40-character"):
            translation._load_translation_model("example/model", revision)


def test_both_model_loads_use_the_same_immutable_revision_without_remote_code():
    tokenizer_class, model_class = Mock(), Mock()
    module = SimpleNamespace(MarianTokenizer=tokenizer_class, MarianMTModel=model_class)
    with patch.dict(sys.modules, {"transformers": module}):
        tokenizer, model = translation._load_translation_model("example/model", "a" * 40)
    for cls in (tokenizer_class, model_class):
        cls.from_pretrained.assert_called_once_with(
            "example/model", revision="a" * 40, trust_remote_code=False
        )
    assert tokenizer is tokenizer_class.from_pretrained.return_value
    assert model is model_class.from_pretrained.return_value


@pytest.mark.parametrize("rows", [[], ["one"], ["one", "two", "invented"]])
def test_model_row_loss_or_addition_is_rejected_before_reconstructing_markdown(tmp_path, rows):
    source = tmp_path / "source.md"
    source.write_text("first requirement\nsecond requirement\n")
    with (
        patch.object(translation, "_load_translation_model", return_value=(Mock(), Mock())),
        patch.object(translation, "translate_text", return_value=rows),
    ):
        with pytest.raises(ValueError, match="zip"):
            translation.translate_markdown_file(source, "fr", "a" * 40)
    assert source.read_text() == "first requirement\nsecond requirement\n"


@pytest.mark.parametrize("explicit_output", [True, False])
def test_structure_only_cli_needs_no_model_and_preserves_exact_bytes(tmp_path, explicit_output):
    source = tmp_path / "source.md"
    source.write_text("# Heading\n---\n\n")
    destination = tmp_path / "specified.md" if explicit_output else tmp_path / "source.fr.md"
    arguments = [str(ROOT / "scripts/translate_checklist.py"), str(source), "fr"]
    if explicit_output:
        arguments.append(str(destination))
    result = subprocess.run(
        [sys.executable, *arguments], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
    assert destination.read_bytes() == source.read_bytes()


@pytest.mark.parametrize("defect", ["missing_source", "missing_revision", "mutable_revision"])
def test_cli_failure_preserves_existing_output(tmp_path, defect):
    source, destination = tmp_path / "source.md", tmp_path / "approved.md"
    if defect != "missing_source":
        source.write_text("A source requirement.\n")
    destination.write_text("previous output")
    arguments = [
        sys.executable,
        str(ROOT / "scripts/translate_checklist.py"),
        str(source),
        "fr",
        str(destination),
    ]
    if defect == "mutable_revision":
        arguments += ["--model-revision", "main"]
    result = subprocess.run(arguments, capture_output=True, text=True, check=False)
    assert result.returncode != 0
    assert destination.read_text() == "previous output"
