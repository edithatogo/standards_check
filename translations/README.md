# Checklist Translations

This project supports two methods for translating checklists: official, human-provided translations and unofficial, on-demand machine translations.

## 1. Official Translations

Official translations are provided by trusted sources and are considered the canonical version for a given language.

### Directory Structure

All checklist markdown files are organized by language using their ISO 639-1 code. The primary English versions are located in the `/markdown/en/` directory.

- `/markdown/en/archetypes/`
- `/markdown/en/variants/`

To add an official translation, create a new directory with the corresponding language code and replicate the `archetypes` and `variants` structure.

For example, a French translation for `consort-2010.md` would be placed at:

- `/markdown/fr/archetypes/consort-2010.md`

## 2. Unofficial (Machine-Generated) Translations

For languages where an official translation is not available, you can generate an unofficial translation using the provided Python script. This script uses a free, open-source model that runs locally on your machine.

### Prerequisites

1.  **Python 3.7+**
2.  **Required Libraries:** Install them using pip and the `requirements.txt` file.
    ```bash
    # From the root of the project
    pip install -r scripts/requirements.txt
    ```
3.  **Internet Connection:** Required for the first run to download the translation model (models are typically 200-300MB). Subsequent runs can be performed offline.

### How to Run the Script

The script takes the source file and the target language code as input.

```bash
python scripts/translate_checklist.py <source_file> <target_language_code> [output_file]
```

**Example:**

To translate the CONSORT 2010 checklist into French:

```bash
python scripts/translate_checklist.py markdown/en/archetypes/consort-2010.md fr
```

This will create a new file named `consort-2010.fr.md` in the same directory.

You can specify a different output path as the third argument if needed.
