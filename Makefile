# STORAGE can be "goinfre" (fast local SSD) or "sgoinfre" (network storage)
STORAGE ?= goinfre

ifeq ($(STORAGE),goinfre)
    BASE_DIR := /goinfre/kvolynsk
else
    BASE_DIR := /home/kvolynsk/sgoinfre
endif

export HF_HOME ?= $(BASE_DIR)/cache/huggingface
export UV_CACHE_DIR ?= $(BASE_DIR)/cache/uv
export UV_PROJECT_ENVIRONMENT ?= $(BASE_DIR)/call-me-maybe/.venv
export HF_HUB_OFFLINE ?= 1
export TRANSFORMERS_OFFLINE ?= 1

PYTHON ?= python3
UV ?= uv
ARGS ?=

.PHONY: install run debug clean lint lint-strict test sync-to-goinfre sync-to-sgoinfre check-env

# Security check to prevent filling up home directory, and auto-symlink update
check-env:
	@[ ! -d .venv ] || [ -L .venv ] || (echo "ERROR: .venv is a heavy local directory! Run: rm -rf .venv" && exit 1)
	@mkdir -p $(BASE_DIR)/call-me-maybe
	@ln -sfn $(UV_PROJECT_ENVIRONMENT) .venv

install: check-env
	$(UV) sync

run: check-env
	$(UV) run $(PYTHON) -m src $(ARGS)

debug: check-env
	$(UV) run $(PYTHON) -m pdb -m src $(ARGS)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint: check-env
	$(UV) run flake8 .
	$(UV) run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict: check-env
	$(UV) run flake8 .
	$(UV) run mypy . --strict

test: check-env
	$(UV) run pytest tests/ -v

# --- Synchronization ---
CACHE_SGOINFRE := /home/kvolynsk/sgoinfre/cache
PROJ_SGOINFRE  := /home/kvolynsk/sgoinfre/call-me-maybe
CACHE_GOINFRE  := /goinfre/kvolynsk/cache
PROJ_GOINFRE   := /goinfre/kvolynsk/call-me-maybe

sync-to-goinfre:
	@mkdir -p $(CACHE_GOINFRE) $(PROJ_GOINFRE)
	@rsync -a $(CACHE_SGOINFRE)/huggingface $(CACHE_SGOINFRE)/uv $(CACHE_GOINFRE)/ 2>/dev/null || true
	@rsync -a $(PROJ_SGOINFRE)/.venv $(PROJ_GOINFRE)/ 2>/dev/null || true
	@echo "✅ Synced sgoinfre -> goinfre"

sync-to-sgoinfre:
	@mkdir -p $(CACHE_SGOINFRE) $(PROJ_SGOINFRE)
	@rsync -a $(CACHE_GOINFRE)/huggingface $(CACHE_GOINFRE)/uv $(CACHE_SGOINFRE)/ 2>/dev/null || true
	@rsync -a $(PROJ_GOINFRE)/.venv $(PROJ_SGOINFRE)/ 2>/dev/null || true
	@echo "✅ Backup saved to sgoinfre"