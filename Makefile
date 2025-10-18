PYTHON := python3
TEST_DIR := tests
SRC_DIR := src
VENV_DIR = .venv
ACTIVATE = $(VENV_DIR)/bin/activate

# Default-Target
.DEFAULT_GOAL := help

create-venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
		echo "Virtual environment created."; \
	else \
		echo "Virtual environment already exists."; \
	fi

use-venv: create-venv
	@echo "Starting new shell with virtual environment..."
	@echo "-----------------------------------------------"
	@. $(ACTIVATE) && exec bash

check-venv-using:
	@if [ -n "$$VIRTUAL_ENV" ]; then \
		echo "Virtual environment is active."; \
	else \
		echo "Virtual environment is not active."; \
	fi

install:
	@echo "Installing dependencies..."
	@if [ -f "$(ACTIVATE)" ]; then \
		bash -c "source $(ACTIVATE) && pip install -r requirements.txt"; \
	else \
		echo "Virtual environment not found. Please run 'make create-venv' first."; \
		exit 1; \
	fi

test:
	@echo "Running all tests with pytest..."
	@if [ -f "$(ACTIVATE)" ]; then \
		bash -c "source $(ACTIVATE) && pytest -v $(TEST_DIR)"; \
	else \
		echo "Virtual environment not found. Please run 'make create-venv' first."; \
		exit 1; \
	fi

fix:
	@echo "Fixing and formatting code (ruff + black)..."
	@if [ -f "$(ACTIVATE)" ]; then \
		bash -c "source $(ACTIVATE) && ruff check $(SRC_DIR) $(TEST_DIR) --fix"; \
		bash -c "source $(ACTIVATE) && black $(SRC_DIR) $(TEST_DIR) scripts"; \
	else \
		echo "Virtual environment not found. Please run 'make create-venv' first."; \
		exit 1; \
	fi

qa-check: fix test
	@echo "QA check completed successfully."

clean:
	@echo "Cleaning cache and build files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .coverage
	@echo "Clean done."

run:
	@python src/core/app.py

help:
	@echo ""
	@echo "Available make commands:"
	@echo "  make run              - Start development environment"
	@echo "  make check-venv-using - Check if virtual environment is active"
	@echo "  make create-venv      - Create virtual environment"
	@echo "  make use-venv         - Activate virtual environment"
	@echo "  make install          - Install Python dependencies"
	@echo "  make test             - Run all unit tests"
	@echo "  make fix              - Auto-fix issues using Ruff and Black"
	@echo "  make qa-check         - Run fix + tests (quality assurance)"
	@echo "  make clean            - Remove cache and temp files"
	@echo ""

