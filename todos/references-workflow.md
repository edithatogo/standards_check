# References Workflow Plan

This document outlines the plan for adding citation metadata to all YAML files in the `source` directory.

## 1. Find Citation Information

For each of the remaining archetype YAML files, find the full citation information. This includes:

*   DOI
*   Full author list
*   Journal/Publisher
*   Publication year
*   Volume, issue, and page numbers

The files that need to be updated are:

*   `source/archetypes/spirit-2025.yml`
*   `source/archetypes/stard-2015.yml`
*   `source/archetypes/tripod-ai-2024.yml`
*   `source/archetypes/coreq-2007.yml`
*   `source/archetypes/tidier-2014.yml`
*   `source/archetypes/srqr-2014.yml`
*   `source/archetypes/squire-2016.yml`
*   `source/archetypes/moose-2000.yml`

## 2. Update YAML Files

Add the citation information to the corresponding YAML file using the `citation` key, following the structure defined in `schemas/sidecar.schema.json`.

## 3. Validate YAML Files

After updating the YAML files, run a validation script to ensure that the new data conforms to the schema. This can be done by extending the existing validation scripts or creating a new one.

## 4. Commit and Push Changes

Once all the YAML files have been updated and validated, commit the changes to the repository and push them to the remote.
