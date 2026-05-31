# Agent Guidelines for OpenEVSE Integration

Welcome, agent! This document contains guidelines and commands for working on the OpenEVSE Home Assistant integration.

## Project Structure
- `custom_components/openevse/`: Core integration code.
  - `manifest.json`: Configuration, requirements, dependencies.
  - `update.py`: Firmware update entities.
  - `sensor.py`, `binary_sensor.py`, `select.py`, `switch.py`, `number.py`, `light.py`, `button.py`: Entity platforms.
  - `services.py`, `services.yaml`: Custom service registration and definitions.
- `tests/`: Integration tests.

## Development Commands

### Testing
Use `tox` to run tests inside a correct virtual environment:
```bash
tox -e py313
```

### Linting & Formatting
The project uses `prek` to run `ruff`, `ruff-format`, `mypy`, `codespell`, and file structure checks:
```bash
.tox/py313/bin/prek run --all-files --show-diff-on-failure
```

## Key Rules & Guidelines

### 1. Top-Level Imports (PLC0415)
To comply with the project linting rules, always place Python imports at the top-level of a module rather than inlining them inside functions or methods (which violates Ruff's `import-outside-toplevel` check).

### 2. Local Testing Against Library Changes
The integration depends on `python-openevse-http`. If you need to make changes to both libraries, you can temporarily edit `requirements.txt` to point to a local directory:
```
-e /path/to/cloned/python-openevse-http
```
**CRITICAL**: Make sure to revert this change back to a published version (e.g., `python-openevse-http==0.4.0`) before staging, committing, or pushing to avoid shipping local paths.
