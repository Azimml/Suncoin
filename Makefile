.PHONY: help install install-dev test lint format fmt-check example api clean

PYTHON ?= python

help:
	@echo "Suncoin - make targets"
	@echo "  install       install the package"
	@echo "  install-dev   install with dev + api extras"
	@echo "  test          run the pytest suite"
	@echo "  lint          run ruff checks"
	@echo "  format        auto-fix with ruff"
	@echo "  example       mine a few example blocks"
	@echo "  api           run the Flask API on :3000"
	@echo "  clean         remove caches and build artifacts"

install:
	$(PYTHON) -m pip install .

install-dev:
	$(PYTHON) -m pip install -e ".[dev,api]"

test:
	$(PYTHON) -m pytest

lint:
	ruff check .

format:
	ruff check --fix .
	ruff format .

example:
	$(PYTHON) examples/mine_blocks.py

api:
	$(PYTHON) -m suncoin.api

clean:
	rm -rf .pytest_cache .ruff_cache build dist *.egg-info suncoin_chain.json
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
