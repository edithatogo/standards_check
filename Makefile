.PHONY: validate build clean scaffold citations html petri-nets index list-tbd

validate:
	bash scripts/validate_repo.sh

build:
	FORMS=eforms bash scripts/build_pandoc.sh
	bash scripts/generate_citations.sh

# --- HTML Generation ---
HTML_DIR := html
HTML_SOURCES := $(patsubst markdown/en/%,%,$(wildcard markdown/en/archetypes/*.md markdown/en/variants/*.md))
HTML_SOURCES += $(patsubst markdown/%,%,$(wildcard markdown/archetypes/*.md markdown/variants/*.md))
HTML_FILES := $(sort $(patsubst %.md,$(HTML_DIR)/%.html,$(HTML_SOURCES)))
# Prefer the maintained English corpus when a legacy scaffold has the same name.
vpath %.md markdown/en markdown

html: $(HTML_FILES) ## Generate HTML versions of all checklists
	@echo "--> Generating HTML index..."
	@./scripts/generate_html_index.sh

$(HTML_DIR)/%.html: %.md templates/pandoc/html_template.html
	@mkdir -p "$(@D)"
	@echo "--> Generating HTML for $<"
	@pandoc "$<" \
		--to=html \
		--shift-heading-level-by=1 \
		--template="templates/pandoc/html_template.html" \
		--metadata checklist_page=true \
		--metadata title="$$(sed -n '/^# /{s/^# //;p;q;}' "$<")" \
		--output="$@"

scaffold:
	bash scripts/scaffold_from_index.sh

citations:
	bash scripts/generate_citations.sh

petri-nets:
	bash scripts/generate_petri_nets.sh

index:
	bash scripts/generate_markdown_index.sh

list-tbd:
	bash scripts/list_tbd.sh

clean:
	rm -rf pdf/* latex/* docx/* citations/*
	find . -name ".DS_Store" -delete


# Fast, network-free maintained contract and source regression profile.
.PHONY: quick
quick:
	python -m unittest tests.test_reconcile_authoritative_articles tests.test_jats_checklist_structure tests.test_review_source_receipts tests.test_classical_linguistic_nlp tests.test_linguistic_benchmark tests.test_linguistic_role_scope tests.test_runtime_pin tests.test_directory_workplan tests.test_publication_contract -v
	python -m scripts.publication_contract
	cargo fmt --all -- --check
	node --check api/server.js
	node --check api/cors-options.js
	node --check scripts/generate_api_data.js

.PHONY: install-hooks publication-check
install-hooks:
	python -m pre_commit validate-config
	python -m pre_commit install --install-hooks

publication-check:
	python -m unittest tests.test_directory_workplan tests.test_publication_contract -v
	python -m scripts.publication_contract
