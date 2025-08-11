.PHONY: validate build clean scaffold citations citations

validate:
	bash scripts/validate_repo.sh

build:
	FORMS=eforms bash scripts/build_pandoc.sh
	bash scripts/generate_citations.sh
	bash scripts/generate_citations.sh

# --- HTML Generation ---
HTML_DIR := html
HTML_ARCHETYPES_DIR := $(HTML_DIR)/archetypes
HTML_VARIANTS_DIR := $(HTML_DIR)/variants
MARKDOWN_ARCHETYPES := $(wildcard markdown/archetypes/*.md)
MARKDOWN_VARIANTS := $(wildcard markdown/variants/*.md)
HTML_ARCHETYPE_FILES := $(patsubst markdown/archetypes/%.md,$(HTML_ARCHETYPES_DIR)/%.html,$(MARKDOWN_ARCHETYPES))
HTML_VARIANT_FILES := $(patsubst markdown/variants/%.md,$(HTML_VARIANTS_DIR)/%.html,$(MARKDOWN_VARIANTS))

.PHONY: html
html: $(HTML_ARCHETYPE_FILES) $(HTML_VARIANT_FILES) ## Generate HTML versions of all checklists
	@echo "--> Generating HTML index..."
	@./scripts/generate_html_index.sh

$(HTML_ARCHETYPES_DIR)/%.html: markdown/archetypes/%.md
	@mkdir -p $(HTML_ARCHETYPES_DIR)
	@echo "--> Generating HTML for $<"
	@pandoc $<
		--to=html
		--template=templates/pandoc/html_template.html
		--output=$@

$(HTML_VARIANTS_DIR)/%.html: markdown/variants/%.md
	@mkdir -p $(HTML_VARIANTS_DIR)
	@echo "--> Generating HTML for $<"
	@pandoc $<
		--to=html
		--template=templates/pandoc/html_template.html
		--output=$@

scaffold:
	bash scripts/scaffold_from_index.sh

citations:
	bash scripts/generate_citations.sh

citations:
	bash scripts/generate_citations.sh

petri-nets:
	bash scripts/generate_petri_nets.sh

index:
	bash scripts/generate_markdown_index.sh

list-tbd:
	bash scripts/list_tbd.sh

clean:
	rm -rf pdf/* latex/* docx/* citations/* citations/*
	find . -name ".DS_Store" -delete
.PHONY: validate build scaffold index clean citations

