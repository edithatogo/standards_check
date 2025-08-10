.PHONY: validate build clean scaffold citations citations

validate:
	bash scripts/validate_repo.sh

build:
	bash scripts/build_pandoc.sh
	bash scripts/generate_citations.sh
	bash scripts/generate_citations.sh

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

