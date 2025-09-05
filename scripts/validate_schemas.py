#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Schema Validator
================

This script validates all source YAML files against their corresponding
JSON schemas.

- `source/index.yml` is validated against `schemas/index.schema.json`.
- All other `.yml` files in `source/` are validated against `schemas/sidecar.schema.json`.

Prerequisites:
--------------
1. Python 3.7+
2. Required libraries, which can be installed via pip:
   `pip install -r requirements.txt`

Usage:
------
`python scripts/validate_schemas.py`

"""

import os
import sys
import json
import yaml
from glob import glob
from jsonschema import validate, ValidationError

def validate_yaml_file(file_path, schema_path):
    """Validates a single YAML file against a given schema."""
    print(f"Processing: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if '<kebab-case-id>' in content:
                print(f"  - SKIPPING: {file_path} (template)")
                return True
            data = yaml.safe_load(content)
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        validate(instance=data, schema=schema)
        print(f"  ✓ OK: {file_path} is valid.")
        return True
    except FileNotFoundError as e:
        print(f"  ✗ ERROR: {e.strerror}: {e.filename}")
        return False
    except yaml.YAMLError as e:
        print(f"  ✗ ERROR: Could not parse YAML file. {e}")
        return False
    except ValidationError as e:
        print(f"  ✗ FAILED: {file_path} is not valid.")
        print(f"    - {e.message}")
        return False

def main():
    """Main function to find all YAML files and validate them."""
    print("Starting schema validation...")
    
    all_valid = True

    # Validate index file
    index_file = "source/index.yml"
    index_schema = "schemas/index.schema.json"
    if not validate_yaml_file(index_file, index_schema):
        all_valid = False

    # Validate sidecar files
    sidecar_files = glob(os.path.join("source", "**", "*.yml"), recursive=True)
    sidecar_schema = "schemas/sidecar.schema.json"
    
    for file_path in sidecar_files:
        if os.path.basename(file_path) not in ["index.yml", "_meta.template.yml"]:
            if not validate_yaml_file(file_path, sidecar_schema):
                all_valid = False

    if all_valid:
        print("\n✓ All YAML files are valid.")
        sys.exit(0)
    else:
        print("\n✗ Some YAML files failed validation.")
        sys.exit(1)

if __name__ == "__main__":
    main()
