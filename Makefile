.PHONY: validate build clean scaffold

validate:
	bash scripts/validate_repo.sh

build:
	bash scripts/build_pandoc.sh

scaffold:
	bash scripts/scaffold_from_index.sh

index:
	bash scripts/generate_markdown_index.sh

list-tbd:
	bash scripts/list_tbd.sh

clean:
	rm -rf pdf/* latex/* docx/*
	find . -name ".DS_Store" -delete
.PHONY: validate build scaffold index clean

