---
name: run-tests-and-lint
description: >-
  Use this skill when running unit tests, linting, formatting, type checks, or pre-commit
  validations on the OpenEVSE integration codebase.
---

# Run Tests and Linting Skill

Use this workflow to validate code changes, ensure test coverage, and satisfy repository formatting and type-checking rules.

## Environments and Tooling

- **Testing tool**: `tox` (uses Python 3.13 virtual environment `py313`)
- **Linting tool**: `prek` located inside the tox environment (`.tox/py313/bin/prek`), which runs `ruff`, `ruff-format`, `mypy`, `codespell`, and yaml/file checks.

## Common Workflows

### 1. Run the Full Test Suite
```bash
tox -e py313
```

### 2. Run a Specific Test File or Test Case
To run specific tests quickly without running everything:
```bash
.tox/py313/bin/pytest tests/test_sensor.py
.tox/py313/bin/pytest tests/test_sensor.py -k "test_sensor_name"
```

### 3. Run Linting and Formatting Checks
Run all pre-commit hooks and linters across all repository files:
```bash
.tox/py313/bin/prek run --all-files --show-diff-on-failure
```

If hooks made automated formatting changes (e.g. `ruff-format` or `end-of-file-fixer`), re-run the command once more to ensure everything passes cleanly.

## Key Rules & Gotchas

1. **Top-Level Imports (PLC0415 / `import-outside-toplevel`)**:
   Always place imports at the module level rather than inside methods or functions.
2. **Type Annotations**:
   Ensure all new entity properties, methods, and service handlers pass `mypy custom_components/openevse`.
3. **Async Fixture Scope**:
   Pytest asyncio fixture loop scope is configured as `function`. Ensure async mocks and Home Assistant test fixtures conform to standard Home Assistant test patterns.
