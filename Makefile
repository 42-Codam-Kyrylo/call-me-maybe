
# STORAGE can be "goinfre" (fast local SSD) or "sgoinfre" (network storage)
STORAGE ?= goinfre

# Project-specific path for .venv
GOINFRE_PROJ := /goinfre/kvolynsk/call-me-maybe
SGOINFRE_PROJ := /home/kvolynsk/sgoinfre/call-me-maybe

# Global cache paths
GOINFRE_CACHE := /goinfre/kvolynsk/cache
SGOINFRE_CACHE := /home/kvolynsk/sgoinfre/cache

ifeq ($(STORAGE),goinfre)
    export HF_HOME ?= $(GOINFRE_CACHE)/huggingface
    export UV_CACHE_DIR ?= $(GOINFRE_CACHE)/uv
else
    export HF_HOME ?= $(SGOINFRE_CACHE)/huggingface
    export UV_CACHE_DIR ?= $(SGOINFRE_CACHE)/uv
endif

export HF_HUB_OFFLINE ?= 1
export TRANSFORMERS_OFFLINE ?= 1

PYTHON ?= python3
UV ?= uv

.PHONY: install run run-web debug clean lint lint-strict test use-goinfre use-sgoinfre sync-to-goinfre sync-to-sgoinfre

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

use-goinfre:
	@ln -sfn $(GOINFRE_PROJ)/.venv .venv
	@echo "Switched .venv symlink to GOINFRE (fast local SSD)"

use-sgoinfre:
	@ln -sfn $(SGOINFRE_PROJ)/.venv .venv
	@echo "Switched .venv symlink to SGOINFRE (persistent network storage)"

sync-to-goinfre:
	@mkdir -p $(GOINFRE_CACHE) $(GOINFRE_PROJ)
	@rsync -a $(SGOINFRE_CACHE)/huggingface $(GOINFRE_CACHE)/ 2>/dev/null || true
	@rsync -a $(SGOINFRE_CACHE)/uv $(GOINFRE_CACHE)/ 2>/dev/null || true
	@rsync -a $(SGOINFRE_PROJ)/.venv $(GOINFRE_PROJ)/ 2>/dev/null || true
	@$(MAKE) use-goinfre
	@echo "Synced sgoinfre -> goinfre and switched to goinfre!"

sync-to-sgoinfre:
	@mkdir -p $(SGOINFRE_CACHE) $(SGOINFRE_PROJ)
	@rsync -a $(GOINFRE_CACHE)/huggingface $(SGOINFRE_CACHE)/ 2>/dev/null || true
	@rsync -a $(GOINFRE_CACHE)/uv $(SGOINFRE_CACHE)/ 2>/dev/null || true
	@rsync -a $(GOINFRE_PROJ)/.venv $(SGOINFRE_PROJ)/ 2>/dev/null || true
	@echo "Synced goinfre -> sgoinfre successfully (backup created)!"