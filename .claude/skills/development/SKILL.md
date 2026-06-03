---
name: openevse-development
description: Guide for developing, testing, and linting the OpenEVSE Home Assistant integration.
---

This skill helps Claude Code develop, test, and format code for the OpenEVSE integration.

## Project Structure

- `custom_components/openevse/`: Core integration code.
  - `manifest.json`: Configuration, requirements, dependencies.
  - `update.py`: Firmware update entities.
  - `sensor.py`, `binary_sensor.py`, `select.py`, `switch.py`, `number.py`, `light.py`, `button.py`: Entity platforms.
  - `services.py`, `services.yaml`: Custom service registration and definitions.
- `tests/`: Integration tests.

## Standard Development Workflows

### 1. Testing
Always run the test suite to verify changes:
```bash
tox -e py313
```

### 2. Formatting & Linting
Run `prek` to execute `ruff`, `ruff-format`, `mypy`, `codespell`, and check file structure:
```bash
.tox/py313/bin/prek run --all-files --show-diff-on-failure
```
You should run this before proposing/committing changes to make sure all formatting and code quality checks pass.

## Coding Rules & Guidelines

1. **Top-Level Imports (PLC0415)**
   Always place Python imports at the top-level of a module. Never use inlined imports inside functions or methods (which violates Ruff's `import-outside-toplevel` check).

2. **Local Testing Against Library Changes**
   The integration depends on `python-openevse-http`. To test against local changes in `python-openevse-http`, temporarily edit `requirements.txt` to point to the local checkout:
   ```txt
   -e /path/to/cloned/python-openevse-http
   ```
   **CRITICAL**: You must revert this change back to a published version (e.g., `python-openevse-http==1.0.0`) before committing, staging, or pushing. Do not ship local paths in `requirements.txt` or `manifest.json`.

3. **PR Titles and Templates**
   - Ensure PR titles are semantic (e.g., `chore(deps): bump python-openevse-http to 1.0.0` or `fix: resolve websocket connection error`).
   - Use the repository's PR template (`.github/pull_request_template.md`) for all Pull Request descriptions.
