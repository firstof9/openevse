---
name: bump-dependency
description: >-
  Use this skill when updating dependencies (like python-openevse-http), modifying requirements.txt,
  or testing local library changes against the OpenEVSE integration.
---

# Bump Dependency & Local Development Skill

This skill explains how to manage external dependencies (principally `python-openevse-http`) and safely develop across local clones.

## Local Development with Cloned Dependencies

When testing integration changes alongside unreleased changes in `python-openevse-http`:

1. **Point to Local Clone**:
   Edit `requirements.txt` temporarily:
   ```txt
   -e /path/to/cloned/python-openevse-http
   ```
2. **Re-install in Virtual Environment**:
   ```bash
   .tox/py313/bin/pip install -e /path/to/cloned/python-openevse-http
   ```
3. **CRITICAL Clean Up Before Commit**:
   Never commit a local `-e` path. Before committing, push, or creating a PR:
   - Ensure the upstream library is published to PyPI or tagged appropriately.
   - Revert `requirements.txt` to the pinned release (e.g. `python-openevse-http==0.4.0`).

## Upgrading a Released Dependency

When bumping an upstream dependency version:

1. **Update `manifest.json`**:
   Update the `requirements` array in [custom_components/openevse/manifest.json](file:///custom_components/openevse/manifest.json):
   ```json
   "requirements": ["python-openevse-http==0.5.0"]
   ```
2. **Update `requirements.txt`**:
   Update [requirements.txt](file:///requirements.txt) to match the version in `manifest.json`.
3. **Update Test Environment**:
   Install the updated version in `.tox/py313`:
   ```bash
   .tox/py313/bin/pip install -r requirements.txt
   ```
4. **Run Test Suite & Linters**:
   ```bash
   tox -e py313
   .tox/py313/bin/prek run --all-files --show-diff-on-failure
   ```
