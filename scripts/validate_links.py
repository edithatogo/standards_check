#!/usr/bin/env python

"""
Link and DOI Validator
======================

This script scans all source YAML files, extracts URLs and DOIs,
and checks their validity.

- For URLs, it makes a HEAD request to ensure they are reachable.
- For DOIs, it resolves them using `https://doi.org`.

The script will report any broken links (e.g., 404 Not Found) or
problematic redirects.

Prerequisites:
--------------
1. Python 3.7+
2. Required libraries, which can be installed via pip:
   `pip install -r requirements.txt`

Usage:
------
`python scripts/validate_links.py`

"""

import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from glob import glob

import requests
import yaml

SOURCE_DIR = "source"
DOI_BASE_URL = "https://doi.org"
SUCCESS_STATUS_CODES = [200, 201, 202, 203]
REDIRECT_STATUS_CODES = [301, 302, 307, 308]
WARNING_STATUS_CODES = [403]  # Treat 403 Forbidden as a warning
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


def validate_url(url, file_path):
    """Validates a single URL with retries."""
    if not url or not url.startswith("http"):
        return None  # Skip empty or invalid URLs

    for attempt in range(MAX_RETRIES):
        try:
            # Use a timeout to avoid hanging on unresponsive servers
            response = requests.head(url, allow_redirects=True, timeout=10)
            status = response.status_code

            if status in SUCCESS_STATUS_CODES:
                print(f"  ✓ OK ({status}): {url}")
                return None
            elif status in REDIRECT_STATUS_CODES:
                final_url = response.url
                print(f"  ? REDIRECT ({status}): {url} -> {final_url}")
                return {
                    "file": file_path,
                    "url": url,
                    "status": status,
                    "final_url": final_url,
                    "type": "REDIRECT",
                }
            elif status in WARNING_STATUS_CODES:
                print(f"  ! WARNING ({status}): {url} (Access Forbidden)")
                return {"file": file_path, "url": url, "status": status, "type": "WARNING"}
            else:
                print(f"  ✗ FAILED ({status}): {url}")
                return {"file": file_path, "url": url, "status": status, "type": "BROKEN"}

        except requests.RequestException as e:
            print(f"  ✗ ERROR on attempt {attempt + 1}/{MAX_RETRIES}: {url} ({e})")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                return {
                    "file": file_path,
                    "url": url,
                    "status": "ERROR",
                    "error_message": str(e),
                    "type": "ERROR",
                }
    return None


def process_file(file_path):
    """Read one sidecar and return its URL tasks, recording malformed input."""
    print(f"\nProcessing: {file_path}")
    try:
        with open(file_path, encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        if data is None:
            return [], []
        if not isinstance(data, dict):
            raise ValueError("Top-level YAML must be a mapping")
        citation = data.get("citation")
        if citation is None:
            citation = {}
        if not isinstance(citation, dict):
            raise ValueError("citation must be a mapping")
        url = data.get("source_url")
        doi = citation.get("doi")
        if url is not None and not isinstance(url, str):
            raise ValueError("source_url must be a string")
        if doi is not None and not isinstance(doi, str):
            raise ValueError("citation.doi must be a string")
        tasks = [(url, file_path)] if url else []
        if doi:
            tasks.append((f"{DOI_BASE_URL}/{doi}", file_path))
        return tasks, []
    except (OSError, UnicodeError, yaml.YAMLError, ValueError) as error:
        status = "YAML_ERROR" if isinstance(error, yaml.YAMLError) else "INPUT_ERROR"
        print(f"  ✗ ERROR: Could not read or parse YAML file. {error}")
        return [], [
            {
                "file": file_path,
                "url": "N/A",
                "status": status,
                "error_message": str(error),
                "type": "ERROR",
            }
        ]


def check_links_in_files(source_files):
    """Collect sidecars, validate concurrently, and report in input order."""
    broken_links, redirected_links, warning_links = [], [], []
    tasks = []
    for file_path in source_files:
        file_tasks, errors = process_file(file_path)
        tasks.extend(file_tasks)
        broken_links.extend(errors)

    print(f"Found {len(tasks)} links to validate. Validating concurrently...")
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(validate_url, url, path): (url, path) for url, path in tasks}
        for future, (url, file_path) in futures.items():
            try:
                result = future.result()
            except Exception as error:
                result = {
                    "file": file_path,
                    "url": url,
                    "status": "EXCEPTION",
                    "error_message": str(error),
                    "type": "ERROR",
                }
            if not result:
                continue
            if result["type"] in ("BROKEN", "ERROR"):
                broken_links.append(result)
            elif result["type"] == "REDIRECT":
                redirected_links.append(result)
            elif result["type"] == "WARNING":
                warning_links.append(result)
    return broken_links, redirected_links, warning_links


def print_summary(broken_links, redirected_links, warning_links):
    """Prints the validation summary and exits appropriately."""
    print("\n--- Validation Summary ---")
    if not broken_links and not redirected_links and not warning_links:
        print("✓ All links are valid.")
    else:
        if redirected_links:
            print(f"\nFound {len(redirected_links)} redirected links (for review):")
            for link in redirected_links:
                print(f"  - File: {link['file']}")
                print(f"    URL: {link['url']}")
                print(f"    Status: {link['status']} -> {link['final_url']}\n")

        if warning_links:
            print(f"\nFound {len(warning_links)} links with warnings (e.g., 403 Forbidden):")
            for link in warning_links:
                print(f"  - File: {link['file']}")
                print(f"    URL: {link['url']}")
                print(f"    Status: {link['status']}\n")

        if broken_links:
            print(f"\nFound {len(broken_links)} broken or invalid links:")
            for link in broken_links:
                print(f"  - File: {link['file']}")
                print(f"    URL: {link['url']}")
                print(f"    Status: {link['status']}\n")
            sys.exit(1)  # Exit with an error code if links are broken

    print("Validation complete.")


def main():
    """Main function to find all YAML files and validate their links."""
    print(f"Starting link validation in '{SOURCE_DIR}' directory...")

    source_files = glob(os.path.join(SOURCE_DIR, "**", "*.yml"), recursive=True)

    if not source_files:
        print("No YAML files found to validate.")
        sys.exit(0)

    broken_links, redirected_links, warning_links = check_links_in_files(source_files)
    print_summary(broken_links, redirected_links, warning_links)
    sys.exit(0)


if __name__ == "__main__":
    main()
