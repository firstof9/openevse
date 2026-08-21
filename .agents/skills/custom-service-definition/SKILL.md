---
name: custom-service-definition
description: >-
  Use this skill when adding, updating, or removing custom Home Assistant services and service schemas
  for the OpenEVSE integration.
---

# Custom Service Definition Skill

This skill outlines the workflow for registering and handling custom services in the OpenEVSE integration.

## Files Involved

- Service logic & registration: [custom_components/openevse/services.py](file:///custom_components/openevse/services.py)
- Service UI descriptions & schemas: [custom_components/openevse/services.yaml](file:///custom_components/openevse/services.yaml)
- Tests: `tests/test_services.py`

## Implementation Steps

1. **Register Service in `services.py`**:
   - Define service schema using `voluptuous`.
   - Implement the async handler function.
   - Extract device or config entry IDs using Home Assistant helpers.
   - Call the underlying OpenEVSE coordinator/charger API method.
   - Register the service in `async_setup_services(hass)` with proper error handling and logging.

2. **Define UI Metadata in `services.yaml`**:
   - Provide clear English descriptions for the service and all input fields.
   - Define field selectors (e.g. `target: device: integration: openevse`, `number`, `text`, `boolean`, `select`).
   - Specify default values, required fields, and examples.

3. **Add Unit Tests in `tests/test_services.py`**:
   - Test successful service invocations with valid parameters.
   - Test invalid parameters to ensure voluptuous validation fails as expected.
   - Test coordinator/device failure handling (e.g., raise `HomeAssistantError` / `ServiceValidationError` where appropriate).

4. **Verify**:
   - Run tests: `.tox/py313/bin/pytest tests/test_services.py`
   - Run linting: `.tox/py313/bin/prek run --all-files --show-diff-on-failure`
