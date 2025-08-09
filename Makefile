.PHONY: validate build clean scaffold citations

validate:
	bash scripts/validate_repo.sh

build:
	bash scripts/build_pandoc.sh
	bash scripts/generate_citations.sh

scaffold:
	bash scripts/scaffold_from_index.sh

citations:
	bash scripts/generate_citations.sh

index:
	bash scripts/generate_markdown_index.sh

list-tbd:
	bash scripts/list_tbd.sh

clean:
	rm -rf pdf/* latex/* docx/* citations/*
	find . -name ".DS_Store" -delete
.PHONY: validate build scaffold index clean citations

