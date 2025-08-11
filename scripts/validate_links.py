#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
import yaml
import requests
from glob import glob

SOURCE_DIR = "source"
DOI_BASE_URL = "https://doi.org"
SUCCESS_STATUS_CODES = [200, 201, 202, 203]
REDIRECT_STATUS_CODES = [301, 302, 307, 308]

def validate_url(url, file_path):
    """Validates a single URL."""
    if not url or not url.startswith('http'):
        return None  # Skip empty or invalid URLs

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
            return {"file": file_path, "url": url, "status": status, "final_url": final_url, "type": "REDIRECT"}
        else:
            print(f"  ✗ FAILED ({status}): {url}")
            return {"file": file_path, "url": url, "status": status, "type": "BROKEN"}

    except requests.RequestException as e:
        print(f"  ✗ ERROR: {url} ({e})")
        return {"file": file_path, "url": url, "status": "ERROR", "error_message": str(e), "type": "ERROR"}

def main():
    """Main function to find all YAML files and validate their links."""
    print(f"Starting link validation in '{SOURCE_DIR}' directory...")
    
    source_files = glob(os.path.join(SOURCE_DIR, "**", "*.yml"), recursive=True)
    
    if not source_files:
        print("No YAML files found to validate.")
        sys.exit(0)

    broken_links = []
    redirected_links = []

    for file_path in source_files:
        print(f"\nProcessing: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = yaml.safe_load(f)
                if not data:
                    continue

                # Validate source_url
                url_to_check = data.get('source_url')
                if url_to_check:
                    result = validate_url(url_to_check, file_path)
                    if result:
                        if result['type'] == 'BROKEN' or result['type'] == 'ERROR':
                            broken_links.append(result)
                        elif result['type'] == 'REDIRECT':
                            redirected_links.append(result)
                
                # Validate DOI
                doi = data.get('citation', {}).get('doi')
                if doi:
                    doi_url = f"{DOI_BASE_URL}/{doi}"
                    result = validate_url(doi_url, file_path)
                    if result:
                        if result['type'] == 'BROKEN' or result['type'] == 'ERROR':
                            broken_links.append(result)
                        # We typically expect DOIs to redirect, so we don't flag them as warnings
                        # unless the final destination is also broken.

            except yaml.YAMLError as e:
                print(f"  ✗ ERROR: Could not parse YAML file. {e}")
                broken_links.append({"file": file_path, "url": "N/A", "status": "YAML_ERROR", "error_message": str(e), "type": "ERROR"})

    print("\n--- Validation Summary ---")
    if not broken_links and not redirected_links:
        print("✓ All links are valid.")
    else:
        if redirected_links:
            print(f"\nFound {len(redirected_links)} redirected links (for review):")
            for link in redirected_links:
                print(f"  - File: {link['file']}")
                print(f"    URL: {link['url']}")
                print(f"    Status: {link['status']} -> {link['final_url']}\n")

        if broken_links:
            print(f"\nFound {len(broken_links)} broken or invalid links:")
            for link in broken_links:
                print(f"  - File: {link['file']}")
                print(f"    URL: {link['url']}")
                print(f"    Status: {link['status']}\n")
            sys.exit(1) # Exit with an error code if links are broken
            
    print("Validation complete.")
    sys.exit(0)

if __name__ == "__main__":
    main()
