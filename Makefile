
export CACHE_DIR ?= /home/kvolynsk/sgoinfre/call-me-maybe/llm-cache
export HF_HOME ?= $(CACHE_DIR)/huggingface
export UV_CACHE_DIR ?= $(CACHE_DIR)/uv-cache

PYTHON ?= python3
UV ?= uv

.PHONY: install run run-web debug clean lint lint-strict test

install:
	$(UV) sync

ARGS ?=

# uv run python -m src [--functions_definition <function_definition_file>] [--input <input_file>] [--
# output <output_file>]
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