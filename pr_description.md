🧪 Add tests for docx CLI error paths

🎯 **What:**
The `extract_docx.py` file was missing tests for the CLI error paths, specifically the `try-except` block covering DOCX processing exceptions and the command-line argument validation logic.
The CLI script execution inside the `__main__` block was refactored into a `main()` function to allow it to be seamlessly imported and tested without actually running the CLI logic directly during import.
A new test file `tests/test_extract_docx.py` has been created using `pytest` and `unittest.mock`.

📊 **Coverage:**
- `test_main_happy_path`: Tests normal execution without errors.
- `test_main_missing_args`: Tests logic paths executing when argument checks fail (`len(sys.argv) != 2`).
- `test_main_extraction_error`: Tests the `try-except` execution path triggered when the wrapped function (`docx.Document` / `extract_text_from_docx`) throws an error.

✨ **Result:**
All error paths correctly report the expected error (via `mock_exit` asserting `sys.exit(1)` and appropriate printing where needed) and exit correctly. The coverage for the CLI execution paths has been successfully tested across edge cases, making it safer for potential future refactorings without regressions.
