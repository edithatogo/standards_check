# Petri Net Conversion Plan

This document outlines the plan to implement a Petri net conversion workflow.

**Status: Complete.** The final implementation generates hierarchical Petri nets from the canonical Markdown files.

## High-Level Goal

To convert the existing YAML-based checklists into a formal Petri net model (in PNML format). This will enable future process mining, formal verification, and simulation of the reporting standards.

---

## Phase 1: Foundational Setup & Proof-of-Concept (Complete)

This phase focuses on analyzing the checklist structure, selecting the right tools, and creating a script that can convert a single, representative YAML file into a PNML file.

**1. Analyze YAML Structure:**
*   **Action**: Read a sample YAML file (e.g., `source/archetypes/prisma-2020.yml`) to understand its schema.
*   **Objective**: Identify the core elements to be mapped, such as sections, items, sub-items, and their sequential relationships. This analysis will determine how a checklist's structure translates to places, transitions, and arcs in a Petri net.

**2. Tool Selection:**
*   **Action**: Research and select a suitable Python library for creating and exporting Petri nets.
*   **Recommendation**: The `pm4py` library is the industry standard for process mining in Python and has robust support for creating, manipulating, and exporting Petri nets to PNML. We will proceed with this choice unless a significant blocker is found.
*   **Dependencies**: This will require adding `pm4py` and `pyyaml` to the project's dependencies.

**3. Develop Core Conversion Script:**
*   **Action**: Create a new Python script: `scripts/convert_yaml_to_pnml.py`.
*   **Functionality**:
    *   Accept an input YAML file path and an output PNML file path as arguments.
    *   Parse the YAML file.
    *   Programmatically build a Petri net:
        *   Create an initial "Start" place and a final "End" place.
        *   Map each checklist item to a place (representing the state of completion) and a transition (representing the action of completing it).
        *   For this initial version, connect all items in a single, sequential flow based on their order in the YAML file.
    *   Use the chosen library to export the generated net into a valid `.pnml` file.

**4. Proof of Concept:**
*   **Action**: Run the script on a single archetype (e.g., `prisma-2020.yml`) and validate the output.
*   **Verification**: Manually inspect the generated `.pnml` file to ensure it represents a valid, sequential net. A visualizer tool could be used to render the PNML for easier inspection.

---

## Phase 2: Automation and Integration (Complete)

This phase expands the proof-of-concept into a reusable, automated workflow that can process all checklists in the repository.

**1. Generalize the Conversion Script:**
*   **Action**: Refactor `scripts/convert_yaml_to_pnml.py` to handle the variations and complexities found across different YAML files.
*   **Objective**: Ensure the script can correctly parse any checklist from `source/archetypes/` and `source/variants/`.

**2. Create Automation Wrapper:**
*   **Action**: Develop a new shell script, `scripts/generate_petri_nets.sh`.
*   **Functionality**:
    *   Create output directories: `petri-nets/archetypes/` and `petri-nets/variants/`.
    *   Find all `*.yml` files in `source/archetypes` and `source/variants`.
    *   For each YAML file, invoke the Python conversion script, saving the corresponding `.pnml` file in the appropriate output directory.

**3. Integrate into Project Workflow:**
*   **Action**: Add the new `generate_petri_nets.sh` script to the `Makefile`.
*   **Objective**: Create a new `make petri-nets` target that automates the generation of all PNML files. This ensures the Petri nets can be easily regenerated whenever the source YAML files are updated.

---

## Phase 3: Refinement and Visualization (Complete)

This phase focuses on enhancing the model's accuracy and providing visual representations for easier analysis.

**1. Advanced Mapping Logic:**
*   **Action**: Enhance the Python script to model more complex structures if the YAML schema supports it.
*   **Potential Features**:
    *   **Parallelism**: If some checklist items can be completed in any order, model them as parallel branches.
    *   **Hierarchy**: Represent sections and sub-items as nested subnets for a more structured and readable model.
    *   **Conditional Logic**: If the YAML contains conditional items (e.g., "if applicable..."), model these using choice structures (e.g., an "invisible transition" that routes the process down one of several paths).

**2. Generate Visualizations:**
*   **Action**: Extend the `generate_petri_nets.sh` script (or the Python script itself) to generate a visual representation (e.g., a `.png` or `.svg` file) for each Petri net.
*   **Tooling**: `pm4py` has built-in visualization capabilities that rely on `graphviz`. The script could export the visualization directly.
*   **Output**: Store visualizations alongside their PNML files (e.g., `petri-nets/archetypes/prisma-2020.png`).
