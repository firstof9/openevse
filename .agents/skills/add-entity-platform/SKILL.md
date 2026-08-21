---
name: add-entity-platform
description: >-
  Use this skill when adding, modifying, or extending entity platforms (sensors, binary sensors,
  switches, selects, numbers, lights, buttons, updates) in the OpenEVSE Home Assistant integration.
---

# Add or Modify Entity Platform Skill

This skill provides guidelines and patterns for implementing or updating Home Assistant entities in the OpenEVSE integration.

## Architecture & Base Classes

- All OpenEVSE entities inherit from `OpenEVSEEntity` in [custom_components/openevse/entity.py](file:///custom_components/openevse/entity.py).
- Platforms implement standard Home Assistant async setup via `async_setup_entry`:
  - `sensor.py`, `binary_sensor.py`, `select.py`, `switch.py`, `number.py`, `light.py`, `button.py`, `update.py`.

## Implementation Checklist

1. **Entity Definition & Description Data Class**:
   - Use typed dataclass entity descriptions (e.g. `SensorEntityDescription`, `SelectEntityDescription`) defined in the respective platform file or [const.py](file:///custom_components/openevse/const.py).
   - Ensure `translation_key` or `name` is properly set.
   - Use `has_entity_name = True` (inherited from `OpenEVSEEntity`).

2. **Coordinator & Data Updates**:
   - Entities use `OpenEVSEDataUpdateCoordinator` for periodic state updates.
   - Ensure property accessors handle `None` values gracefully when coordinator data is missing or charging states are unavailable.

3. **Constants & Keys**:
   - Add new dictionary keys or configuration constants to [custom_components/openevse/const.py](file:///custom_components/openevse/const.py).

4. **Translations & Strings**:
   - Update [custom_components/openevse/translations/en.json](file:///custom_components/openevse/translations/en.json) (and `strings.json` if present) for new entity names, options, or state attributes.

5. **Unit Tests**:
   - Create or update the corresponding test file under `tests/test_<platform>.py`.
   - Mock coordinator data to verify entity state, available property, device info, and command handling.
   - Test both normal states and edge cases (e.g. unavailable / offline state).

6. **Validation**:
   - Run platform tests: `.tox/py313/bin/pytest tests/test_<platform>.py`
   - Run linting: `.tox/py313/bin/prek run --all-files --show-diff-on-failure`
