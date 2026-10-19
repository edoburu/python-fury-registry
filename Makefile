.PHONY: help install build test
## Makefile commands:

help:
	@grep -F -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | perl -pe 's/^([\w\-]+):(.+?)##/"  $$1:" . " " x (20 - length($$1))/e' | perl -pe 's/^## ?//'

install:           ## Install dependencies in a local virtualenv
	uv sync --dev

build:             ## Build the package
	uv run -m build
	uv run -m zipfile -l dist/*.whl

test:              ## Run the testsuite
	uv run pytest -v
