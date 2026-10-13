# Contributing to OpenEVSE

Thank you for your interest in contributing to the OpenEVSE Home Assistant integration!

---

## Code of Conduct & Guidelines

Please adhere to standard open source etiquette and respect fellow contributors.

---

## Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/firstof9/openevse.git
   cd openevse
   ```
2. Create and activate a Python 3.13 virtual environment:
   ```bash
   python3.13 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements_test.txt
   ```
3. Run tests via tox:
   ```bash
   tox -e py313
   ```
4. Run pre-commit checks:
   ```bash
   .tox/py313/bin/prek run --all-files
   ```

---

## Documentation Development

The documentation site is built using VitePress:

1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the local preview server:
   ```bash
   npm run docs:dev
   ```
3. Build the static site:
   ```bash
   npm run docs:build
   ```

---

## Pull Request Guidelines

- Ensure your branch is up to date with `main`.
- Follow the repository template at `.github/pull_request_template.md`.
- Keep Python imports at module top-level (`PLC0415` compliance).
- Include unit tests in `tests/` for new functionality.
