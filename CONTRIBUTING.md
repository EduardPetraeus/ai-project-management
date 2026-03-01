# Contributing to AI Project Management

Thank you for your interest in contributing to the YAML-based task engine for agentic development.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/EduardPetraeus/ai-project-management.git
   cd ai-project-management
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install in development mode:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run the test suite:**
   ```bash
   make test
   ```

5. **Run the linter:**
   ```bash
   make lint
   ```

## Code Style

- **Python:** Follow PEP 8. We use `ruff` for linting and formatting.
  - `snake_case` for variables and functions
  - `PascalCase` for classes
  - Line length: 120 characters
- **YAML files:** Must validate against their corresponding JSON schema in `schemas/`.
- **File names:** `kebab-case` for documentation, `snake_case` for Python modules.
- **Language:** All code, comments, docstrings, and documentation must be in English.

## Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes.** Ensure:
   - All tests pass: `make test`
   - Linting passes: `make lint`
   - YAML validation passes: `make validate`

3. **Write tests** for any new functionality. Target 80%+ code coverage.

4. **Commit** with clear, descriptive messages:
   ```
   feat: add support for milestone tracking
   fix: handle empty backlog directory gracefully
   docs: update CLI usage examples
   ```

## Pull Request Process

1. Push your branch and open a PR against `main`.
2. Fill in the PR template with a description of changes.
3. Ensure all CI checks pass (lint, test, validate).
4. Request a review. The maintainer will review within a few days.
5. Address any feedback, then the PR will be merged.

## Adding New Schemas

When adding a new YAML template:

1. Create the template in `templates/`.
2. Create a matching JSON schema in `schemas/` using JSON Schema draft 2020-12.
3. Add a schema detector in `src/ai_pm/validator.py`.
4. Add validation tests in `tests/test_schemas.py`.
5. Add an example in `examples/`.

## Reporting Issues

- Use GitHub Issues for bug reports and feature requests.
- Include reproduction steps for bugs.
- Include your Python version and OS.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.
