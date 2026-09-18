BASE_DIR := /goinfre/$(USER)
export HF_HOME := $(BASE_DIR)/cache/huggingface
export UV_CACHE_DIR := $(BASE_DIR)/cache/uv
export UV_PROJECT_ENVIRONMENT := $(BASE_DIR)/call-me-maybe/.venv

PYTHON := python3
UV := uv
ARGS ?=

.PHONY: install run debug clean lint lint-strict test

install:
	@mkdir -p $(BASE_DIR)/call-me-maybe
	@ln -sfn $(UV_PROJECT_ENVIRONMENT) .venv
	$(UV) sync

run:
	$(UV) run $(PYTHON) -m src $(ARGS)

debug:
	$(UV) run $(PYTHON) -m pdb -m src $(ARGS)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	$(UV) run flake8 .
	$(UV) run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(UV) run flake8 .
	$(UV) run mypy . --strict

test:
	$(UV) run pytest tests/ -v