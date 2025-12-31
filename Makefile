# Goated - Go stdlib for Python
# Prefer `just` for development (more features), this Makefile is for compatibility

.PHONY: all setup sync check test lint fmt typecheck bench build clean help

# Detect OS
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
	LIB_EXT := so
endif
ifeq ($(UNAME_S),Darwin)
	LIB_EXT := dylib
endif
ifeq ($(OS),Windows_NT)
	LIB_EXT := dll
endif

LIB_NAME := libgoated.$(LIB_EXT)

# ═══════════════════════════════════════════════════════════════════════════════
# QUICK START
# ═══════════════════════════════════════════════════════════════════════════════

all: check

setup:
	uv venv
	uv pip install -e ".[dev]"
	@echo "✓ Ready! Run 'make test' to verify"

sync:
	uv pip install -e ".[dev]" --reinstall-package goated

# ═══════════════════════════════════════════════════════════════════════════════
# DEVELOPMENT
# ═══════════════════════════════════════════════════════════════════════════════

check: lint typecheck test-fast
	@echo "✓ All checks passed"

check-all: lint typecheck test
	@echo "✓ Full check passed"

dev: fmt lint typecheck test
	@echo "✓ Dev cycle complete"

# ═══════════════════════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════════════════════

test:
	uv run pytest tests/ -q

test-fast:
	uv run pytest tests/ -q --tb=line -x

test-v:
	uv run pytest tests/ -v

test-cov:
	uv run pytest tests/ --cov=goated --cov-report=term-missing

# ═══════════════════════════════════════════════════════════════════════════════
# CODE QUALITY
# ═══════════════════════════════════════════════════════════════════════════════

lint:
	uv run ruff check goated/ tests/ benchmarks/ examples/

lint-fix:
	uv run ruff check goated/ tests/ benchmarks/ examples/ --fix

typecheck:
	uv run mypy goated/ --ignore-missing-imports --no-error-summary

fmt:
	uv run ruff format goated/ tests/ benchmarks/ examples/

# ═══════════════════════════════════════════════════════════════════════════════
# BENCHMARKS
# ═══════════════════════════════════════════════════════════════════════════════

bench:
	uv run python benchmarks/bench_stdlib.py
	uv run python benchmarks/bench_concurrency.py

bench-stdlib:
	uv run python benchmarks/bench_stdlib.py

bench-concurrency:
	uv run python benchmarks/bench_concurrency.py

# ═══════════════════════════════════════════════════════════════════════════════
# BUILD
# ═══════════════════════════════════════════════════════════════════════════════

build: goated/$(LIB_NAME)

goated/$(LIB_NAME): golib/*.go
	@echo "Building Go shared library..."
	cd golib && go build -buildmode=c-shared -o ../goated/$(LIB_NAME) .
	@echo "✓ Built goated/$(LIB_NAME)"

# ═══════════════════════════════════════════════════════════════════════════════
# GO
# ═══════════════════════════════════════════════════════════════════════════════

go-fmt:
	cd golib && go fmt ./...

go-test:
	cd golib && go test -v ./...

go-tidy:
	cd golib && go mod tidy

# ═══════════════════════════════════════════════════════════════════════════════
# GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

gen-build:
	cd generator && go build -o goated-gen .

# ═══════════════════════════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════════════════════════

clean:
	rm -f goated/*.so goated/*.dylib goated/*.dll goated/*.h
	rm -rf build/ dist/ *.egg-info/ goated.egg-info/
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/ .benchmarks/
	rm -rf htmlcov/ .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleaned"

clean-all: clean
	rm -rf .venv/

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

repl:
	uv run python -c "from goated.std import *; from goated import Ok, Err, Result" -i

info:
	@echo "Package: goated"
	@uv run python -c "import goated; print('Version:', goated.__version__)"
	@uv run python -c "from goated._core import is_library_available; print('Go FFI:', is_library_available())"

help:
	@echo "Goated - Go stdlib for Python"
	@echo ""
	@echo "Quick start:"
	@echo "  make setup     Setup development environment"
	@echo "  make check     Run lint + typecheck + tests"
	@echo "  make dev       Format + lint + typecheck + tests"
	@echo ""
	@echo "Testing:"
	@echo "  make test      Run all tests"
	@echo "  make test-fast Run tests (fast, stop on first failure)"
	@echo "  make test-cov  Run tests with coverage"
	@echo ""
	@echo "Quality:"
	@echo "  make lint      Run linter"
	@echo "  make fmt       Format code"
	@echo "  make typecheck Run type checker"
	@echo ""
	@echo "Other:"
	@echo "  make bench     Run benchmarks"
	@echo "  make build     Build Go shared library"
	@echo "  make clean     Clean build artifacts"
	@echo ""
	@echo "Tip: Use 'just' for more commands (just --list)"
