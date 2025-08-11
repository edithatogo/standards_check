#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unofficial Checklist Translation Script
========================================

This script translates a markdown checklist file from English to a specified
target language using a pre-trained machine learning model from Hugging Face.

It runs entirely locally, requiring no API keys or subscriptions.

Prerequisites:
--------------
1. Python 3.7+
2. An active internet connection (for the first run to download the model).
3. Required libraries, which can be installed via pip:
   `pip install -r requirements.txt`

Usage:
------
`python scripts/translate_checklist.py <source_file> <target_language_code> [output_file]`

Arguments:
----------
- `source_file`: Path to the source English markdown file.
- `target_language_code`: An ISO 639-1 code for the target language (e.g., 'fr', 'es', 'de').
- `output_file` (optional): The path to save the translated file. If not provided,
  it will be saved in the same directory as the source with the language code
  appended (e.g., `my-checklist.fr.md`).

Example:
--------
`python scripts/translate_checklist.py markdown/en/archetypes/consort-2010.md fr`

"""

import sys
import os
from transformers import MarianMTModel, MarianTokenizer

def translate_text(text, model, tokenizer):
    """Translates a batch of text."""
    if not text or not any(line.strip() for line in text):
        return ""
    translated_tokens = model.generate(**tokenizer(text, return_tensors="pt", padding=True))
    return [tokenizer.decode(t, skip_special_tokens=True) for t in translated_tokens]

def translate_markdown_file(source_path, target_lang):
    """
    Translates a markdown file line by line, preserving structure.
    """
    model_name = f'Helsinki-NLP/opus-mt-en-{target_lang}'
    print(f"Loading model: {model_name}...")

    try:
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
    except OSError:
        print(f"Error: Model for target language '{target_lang}' not found.")
        print("Please check the Hugging Face model hub for available 'Helsinki-NLP/opus-mt-en-*' models.")
        sys.exit(1)

    print("Reading source file...")
    with open(source_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    translated_lines = []
    batch_to_translate = []
    line_indices_to_translate = []

    print("Processing markdown and preparing for translation...")
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        # Translate lines that contain text but are not just headings or separators
        if stripped_line and not stripped_line.startswith('#') and not stripped_line == '---':
            batch_to_translate.append(stripped_line)
            line_indices_to_translate.append(i)

    print(f"Translating {len(batch_to_translate)} lines...")
    translated_text_batch = translate_text(batch_to_translate, model, tokenizer)

    # Create a map of original line index to translated text
    translation_map = dict(zip(line_indices_to_translate, translated_text_batch))

    # Reconstruct the file
    for i, line in enumerate(lines):
        if i in translation_map:
            # Preserve original indentation
            leading_whitespace = line[:len(line) - len(line.lstrip())]
            translated_lines.append(leading_whitespace + translation_map[i] + '\n')
        else:
            translated_lines.append(line)

    return "".join(translated_lines)


if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python translate_checklist.py <source_file> <target_language_code> [output_file]")
        sys.exit(1)

    source_file = sys.argv[1]
    target_language = sys.argv[2]
    output_file = None

    if len(sys.argv) == 4:
        output_file = sys.argv[3]
    else:
        base, ext = os.path.splitext(source_file)
        output_file = f"{base}.{target_language}{ext}"

    if not os.path.exists(source_file):
        print(f"Error: Source file not found at '{source_file}'")
        sys.exit(1)

    print(f"Starting translation for '{source_file}' to '{target_language}'...")
    translated_content = translate_markdown_file(source_file, target_language)

    print(f"Writing translated content to '{output_file}'...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(translated_content)

    print("Translation complete!")
