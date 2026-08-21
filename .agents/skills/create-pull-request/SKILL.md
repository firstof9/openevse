---
name: create-pull-request
description: >-
  Use this skill when preparing or creating a Pull Request (PR) for this repository,
  to ensure PRs follow the repository template, style guidelines, and checklists.
---

# Create Pull Request Skill

When creating or proposing a Pull Request (PR) for this repository, you **must** use and follow the repository's PR template located at [.github/pull_request_template.md](file:///.github/pull_request_template.md).

## PR Workflow & Requirements

1. **Check the Template**:
   - Read and format the PR body using the structure from [.github/pull_request_template.md](file:///.github/pull_request_template.md).

2. **Fill in Required Sections**:
   - **Description**: Provide a clear summary of the changes and motivation. Reference any related issues (e.g., `Fixes #123`).
   - **Type of change**: Select only the relevant change types (delete or uncheck irrelevant ones):
     - Bug fix
     - New feature
     - Breaking change
     - Code quality / Refactoring
     - Documentation update
   - **Checklist**: Ensure all items apply or have been completed:
     - Code follows project style guidelines.
     - Self-review performed.
     - Code commented where necessary.
     - Documentation updated if needed.
     - No new warnings generated.
     - Unit tests added/updated and passing locally.
     - Any dependent library changes have been published/merged (no local paths in `requirements.txt`).

3. **Pre-PR Verification**:
   - Run tests: `tox -e py313`
   - Run linting: `.tox/py313/bin/prek run --all-files --show-diff-on-failure`
