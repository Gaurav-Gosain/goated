# Contributing to GOATED

Thank you for your interest in contributing to GOATED! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Commit Messages](#commit-messages)

## Code of Conduct

Be respectful and constructive. We're all here to build something great.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/goated`
3. Add upstream remote: `git remote add upstream https://github.com/Gaurav-Gosain/goated`
4. Create a branch: `git checkout -b feature/your-feature-name`

## Development Setup

### Prerequisites

- Python 3.10+
- Go 1.21+ (for building the shared library)
- [just](https://github.com/casey/just) command runner (recommended)
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### Quick Setup

```bash
# Using just (recommended)
just setup

# Or manually
python -m venv .venv
source .venv/bin/activate  # or .venv/Scripts/activate on Windows
pip install -e ".[dev]"
```

### Building the Go Shared Library

```bash
just build        # Development build
just build-release  # Optimized build
```

### Running Tests

```bash
just test         # Run all tests
just test-fast    # Run tests without verbose output
just test-v       # Run tests with verbose output
just test-k PATTERN  # Run tests matching pattern
just test-mod MODULE  # Run tests for specific module
```

### Running Benchmarks

```bash
just bench-quick      # Quick benchmark comparison
just bench-concurrency  # Concurrency benchmarks
just bench-stdlib     # Standard library benchmarks
```

## Code Style

### Python

We use [ruff](https://github.com/astral-sh/ruff) for linting and formatting.

```bash
just fmt      # Format code
just lint     # Run linter
just lint-fix # Fix auto-fixable issues
```

**Key style points:**

- Line length: 100 characters
- Use type hints everywhere
- Follow Go naming conventions for API functions (PascalCase for exported functions)
- Use snake_case for internal Python functions
- No `as any`, `@ts-ignore`, or type suppression

### Go (for shared library)

```bash
just go-fmt   # Format Go code
just go-check # Check Go code
```

### Type Checking

```bash
just typecheck        # Run mypy
just typecheck-strict # Run mypy in strict mode
```

All code must pass type checking with mypy strict mode.

## Testing

### Test Requirements

- All new features must have tests
- All bug fixes should include a regression test
- Tests must pass on Python 3.10, 3.11, and 3.12
- Aim for high test coverage

### Writing Tests

```python
# tests/test_module.py
import pytest
from goated.std import module

def test_feature_description():
    """Test that feature does X when given Y."""
    result = module.Function(input)
    assert result == expected

def test_error_handling():
    """Test that proper error is returned for invalid input."""
    result = module.Function(invalid_input)
    assert result.is_err()
```

### Running CI Locally

```bash
just ci  # Runs clean, setup, lint, typecheck, and all tests
```

## Pull Request Process

### Before Submitting

1. **Run the full CI locally**: `just ci`
2. **Update documentation** if needed
3. **Add tests** for new functionality
4. **Update CHANGELOG.md** under `[Unreleased]`

### PR Guidelines

1. **Title**: Use a clear, descriptive title
   - `feat: Add support for X`
   - `fix: Handle edge case in Y`
   - `docs: Update README with Z`
   - `perf: Optimize W operation`

2. **Description**: Include:
   - What the PR does
   - Why it's needed
   - How to test it
   - Any breaking changes

3. **Size**: Keep PRs focused and reasonably sized
   - Large changes should be split into smaller PRs
   - Each PR should do one thing well

### Review Process

1. At least one maintainer approval required
2. All CI checks must pass
3. No unresolved conversations
4. Squash and merge preferred

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(runtime): add FastChan for high-throughput scenarios

fix(filepath): handle symlinks correctly in EvalSymlinks

docs: add CONTRIBUTING.md

perf(chan): use deque+Condition instead of queue.Queue

Improves channel throughput by 1.5x for high-volume scenarios.
```

## Architecture Overview

See [ARCHITECTURE.md](ARCHITECTURE.md) for details on:
- FFI design and handle-based approach
- M:N scheduler and work-stealing
- Memory management and GC safety

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas

---

Thank you for contributing! 🐐
