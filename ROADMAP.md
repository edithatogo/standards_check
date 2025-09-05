### Roadmap

#### Data Quality Initiative
- [ ] **Fix Broken Links:** Systematically investigate and correct the broken and redirected links identified by the `validate_links.py` script.
- [ ] **Schema Validation:** Enhance validation to ensure all source YAML files conform to the project's schemas, preventing data entry errors.

#### Tooling & Automation
- [ ] **Fully Implement `find_latest_checklist.py`:** Integrate a live web search tool to make the script fully functional for discovering new checklist versions.
- [x] **Automated Documentation Generation:** Create a script to automatically generate a user-friendly HTML documentation site from the checklist data.
  - *Note: Core functionality is implemented via the `Makefile` and `pandoc` for building individual pages from Markdown sources, and `scripts/generate_html_index.sh` for the main index. The system is functional for basic HTML site generation.*

#### Content Expansion
- [ ] **Ingest New Checklists:** Use the enhanced `find_latest_checklist.py` to identify, ingest, and process at least one new checklist.