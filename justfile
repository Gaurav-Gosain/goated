# Goated - Go stdlib for Python
# Run `just` to see all commands

set dotenv-load := false
set positional-arguments := true

# Default - show help
default:
    @just --list --unsorted

# ══════════════════════════════════════════════════════════════════════════════
# QUICK START
# ══════════════════════════════════════════════════════════════════════════════

# Setup everything (first time)
setup:
    uv venv
    uv pip install -e ".[dev]"
    @echo "✓ Ready! Run 'just test' to verify"

# Fast reinstall after code changes
sync:
    uv pip install -e ".[dev]" --reinstall-package goated

# ══════════════════════════════════════════════════════════════════════════════
# DEVELOPMENT WORKFLOW
# ══════════════════════════════════════════════════════════════════════════════

# Run quick validation (lint + typecheck + fast tests)
check: lint typecheck test-fast
    @echo "✓ All checks passed"

# Run full validation (lint + typecheck + all tests)
check-all: lint typecheck test
    @echo "✓ Full check passed"

# Format, lint, typecheck, test - the full cycle
dev: fmt lint typecheck test
    @echo "✓ Dev cycle complete"

# Watch mode - run tests on file changes
watch:
    uv run watchfiles "just test-fast" goated/ tests/

# Watch with full checks
watch-full:
    uv run watchfiles "just check" goated/ tests/

# ══════════════════════════════════════════════════════════════════════════════
# TESTING
# ══════════════════════════════════════════════════════════════════════════════

# Run all tests
test *ARGS:
    uv run pytest tests/ -q {{ ARGS }}

# Run tests (fast - no verbose)
test-fast:
    uv run pytest tests/ -q --tb=line -x

# Run tests with verbose output
test-v:
    uv run pytest tests/ -v

# Run tests with coverage
test-cov:
    uv run pytest tests/ --cov=goated --cov-report=term-missing --cov-report=html
    @echo "Coverage report: htmlcov/index.html"

# Run specific test file
test-file FILE:
    uv run pytest {{ FILE }} -v

# Run tests matching pattern
test-k PATTERN:
    uv run pytest tests/ -v -k "{{ PATTERN }}"

# Run tests for a specific module (e.g., just test-mod strings)
test-mod MOD:
    uv run pytest tests/test_{{ MOD }}.py -v

# ══════════════════════════════════════════════════════════════════════════════
# CODE QUALITY
# ══════════════════════════════════════════════════════════════════════════════

# Run linter
lint:
    uv run ruff check goated/ tests/ benchmarks/ examples/

# Run linter and fix auto-fixable issues
lint-fix:
    uv run ruff check goated/ tests/ benchmarks/ examples/ --fix

# Run type checker
typecheck:
    uv run mypy goated/ --ignore-missing-imports --no-error-summary

# Run type checker (strict mode)
typecheck-strict:
    uv run mypy goated/ --strict --ignore-missing-imports

# Format code
fmt:
    uv run ruff format goated/ tests/ benchmarks/ examples/

# Check formatting without changing files
fmt-check:
    uv run ruff format goated/ tests/ benchmarks/ examples/ --check

# ══════════════════════════════════════════════════════════════════════════════
# BENCHMARKS
# ══════════════════════════════════════════════════════════════════════════════

# Run all benchmarks
bench:
    @echo "═══════════════════════════════════════════════════════════════"
    @echo "  STDLIB BENCHMARKS (single operations)"
    @echo "═══════════════════════════════════════════════════════════════"
    uv run python benchmarks/bench_stdlib.py
    @echo ""
    @echo "═══════════════════════════════════════════════════════════════"
    @echo "  BATCH BENCHMARKS (parallel processing - where Go shines)"  
    @echo "═══════════════════════════════════════════════════════════════"
    uv run python benchmarks/bench_batch.py

# Run stdlib benchmarks (single operations)
bench-stdlib:
    uv run python benchmarks/bench_stdlib.py

# Run batch/parallel benchmarks (where Go FFI wins)
bench-batch:
    uv run python benchmarks/bench_batch.py

# Run scaled benchmarks (finding crossover points)
bench-scaled:
    uv run python benchmarks/bench_scaled.py

# Run concurrency benchmarks
bench-concurrency:
    uv run python benchmarks/bench_concurrency.py

# Run pytest benchmarks (if any)
bench-pytest:
    uv run pytest tests/ -v --benchmark-only --benchmark-sort=mean

# Quick benchmark comparison
bench-quick:
    uv run python benchmarks/bench_quick.py

# ══════════════════════════════════════════════════════════════════════════════
# BUILD
# ══════════════════════════════════════════════════════════════════════════════

# Build Go shared library
build:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Building Go shared library..."
    cd golib
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        go build -buildmode=c-shared -o ../goated/libgoated.so .
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        go build -buildmode=c-shared -o ../goated/libgoated.dylib .
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        go build -buildmode=c-shared -o ../goated/libgoated.dll .
    fi
    echo "✓ Build complete"

# Build with optimizations
build-release:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Building optimized Go shared library..."
    cd golib
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        go build -buildmode=c-shared -ldflags="-s -w" -o ../goated/libgoated.so .
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        go build -buildmode=c-shared -ldflags="-s -w" -o ../goated/libgoated.dylib .
    fi
    echo "✓ Release build complete"

# ══════════════════════════════════════════════════════════════════════════════
# CLEANUP
# ══════════════════════════════════════════════════════════════════════════════

# Clean build artifacts
clean:
    rm -f goated/*.so goated/*.dylib goated/*.dll goated/*.h
    rm -rf build/ dist/ *.egg-info/ goated.egg-info/
    rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/ .benchmarks/
    rm -rf htmlcov/ .coverage
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    @echo "✓ Cleaned"

# Deep clean (includes venv)
clean-all: clean
    rm -rf .venv/
    @echo "✓ Deep cleaned (run 'just setup' to reinstall)"

# ══════════════════════════════════════════════════════════════════════════════
# GO DEVELOPMENT
# ══════════════════════════════════════════════════════════════════════════════

# Format Go code
go-fmt:
    cd golib && go fmt ./...

# Run Go tests
go-test:
    cd golib && go test -v ./...

# Tidy Go modules
go-tidy:
    cd golib && go mod tidy

# Check Go code
go-check: go-fmt go-tidy
    cd golib && go vet ./...

# ══════════════════════════════════════════════════════════════════════════════
# GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

# Build the code generator
gen-build:
    cd generator && go build -o goated-gen .

# Generate bindings for a package
gen PKG:
    cd generator && ./goated-gen -pkg {{ PKG }}

# ══════════════════════════════════════════════════════════════════════════════
# RELEASE
# ══════════════════════════════════════════════════════════════════════════════

# Build distribution packages
dist: clean check-all
    uv pip install build
    uv run python -m build
    @echo "✓ Built dist/"

# Check package before upload
dist-check: dist
    uv pip install twine
    uv run twine check dist/*

# ══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ══════════════════════════════════════════════════════════════════════════════

# Run Python REPL with goated loaded
repl:
    uv run python -c "from goated.std import *; from goated import Ok, Err, Result; print('goated loaded - try: strings.Contains(\"hello\", \"ell\")')" -i

# Run example script
example FILE="examples/basic_strings.py":
    uv run python {{ FILE }}

# Run all examples
examples:
    #!/usr/bin/env bash
    for f in examples/*.py; do
        echo "═══ Running $f ═══"
        uv run python "$f" || true
        echo ""
    done

# Show package info
info:
    @echo "Package: goated"
    @uv run python -c "import goated; print(f'Version: {goated.__version__}')"
    @uv run python -c "from goated._core import is_library_available; print(f'Go FFI: {is_library_available()}')"
    @echo "Python: $(uv run python --version | cut -d' ' -f2)"
    @echo "Tests: $(find tests -name 'test_*.py' | wc -l) files"

# Count lines of code
loc:
    @echo "Lines of code:"
    @echo "  Python (goated/): $(find goated -name '*.py' -exec cat {} + | wc -l)"
    @echo "  Tests:            $(find tests -name '*.py' -exec cat {} + | wc -l)"
    @echo "  Go (golib/):      $(find golib -name '*.go' -exec cat {} + 2>/dev/null | wc -l)"
    @echo "  Examples:         $(find examples -name '*.py' -exec cat {} + | wc -l)"
    @echo "  Benchmarks:       $(find benchmarks -name '*.py' -exec cat {} + | wc -l)"

# Show test coverage by module
cov-report:
    uv run pytest tests/ --cov=goated --cov-report=term-missing --cov-report=html -q
    @echo ""
    @echo "HTML report: htmlcov/index.html"

# Verify everything works (CI simulation)
ci: clean
    just setup
    just check-all
    just bench-quick
    @echo "✓ CI simulation passed"
