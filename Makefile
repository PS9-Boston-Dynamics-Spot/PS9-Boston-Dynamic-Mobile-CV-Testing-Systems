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

# Im Docker-Container: Startet neue Shell-Session in vorhandenem Terminal
use-venv: create-venv
	@echo "Starting new shell with virtual environment..."
	@echo "-----------------------------------------------"
	@bash -c "source $(ACTIVATE) && exec bash"

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

lint:
	@echo "Running linter (flake8)..."
	@if [ -f "$(ACTIVATE)" ]; then \
		bash -c "source $(ACTIVATE) && flake8 $(SRC_DIR) $(TEST_DIR) --count --select=E9,F63,F7,F82 --show-source --statistics"; \
	else \
		echo "Virtual environment not found. Please run 'make create-venv' first."; \
		exit 1; \
	fi

format:
	@echo "Formatting code (black)..."
	@if [ -f "$(ACTIVATE)" ]; then \
		bash -c "source $(ACTIVATE) && black $(SRC_DIR) $(TEST_DIR) scripts"; \
	else \
		echo "Virtual environment not found. Please run 'make create-venv' first."; \
		exit 1; \
	fi

qa-check: format lint test
	@echo "QA check completed successfully."

clean:
	@echo "Cleaning cache and build files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .coverage
	@echo "Clean done."

# Haupt-Command: Führt alle Schritte aus und startet die virtuelle Umgebung
run: create-venv install
	@echo ""
	@echo "All checks passed! Starting virtual environment..."
	@echo "You can now start developing!"
	@echo "-----------------------------------------------"
	@bash -c "source $(ACTIVATE) && exec bash"

help:
	@echo ""
	@echo "Available make commands:"
	@echo "  make run         - Complete setup (venv + install + tests + lint) and start shell"
	@echo "  make check-venv-using  - Check if virtual environment is active"
	@echo "  make create-venv - Create virtual environment"
	@echo "  make use-venv    - Activate virtual environment"
	@echo "  make install     - Install Python dependencies"
	@echo "  make test        - Run all unit tests"
	@echo "  make lint        - Run static code analysis"
	@echo "  make format      - Auto-format code with black"
	@echo "  make qa-check    - Run lint + tests (quality assurance)"
	@echo "  make clean       - Remove cache and temp files"
	@echo ""