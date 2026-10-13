# Architecture & Internals

This section describes the internal architecture and design patterns of the OpenEVSE integration for contributors, developers, and advanced users.

---

## Directory Layout

```text
custom_components/openevse/
├── __init__.py          # Entry setup, coordinator, WebSocket listeners
├── manifest.json        # Integration metadata & dependencies
├── const.py             # Domain constants, entity descriptions, service names
├── entity.py            # Base entity classes and typed EntityDescription dataclasses
├── config_flow.py       # UI config flow (setup, reconfigure & options)
├── logger.py            # Custom logger adapter (adds device name prefix)
├── diagnostics.py       # Home Assistant diagnostics support
│
├── sensor.py            # Sensor platform
├── binary_sensor.py     # Binary sensor platform
├── switch.py            # Switch platform
├── select.py            # Select platform
├── number.py            # Number platform
├── light.py             # Light platform (LED brightness)
├── button.py            # Button platform (reset, restart, stuck-relay recovery)
├── calendar.py          # Calendar platform (scheduling)
├── update.py            # Update platform (OTA firmware tracking)
│
├── services.py          # Custom service handlers
├── services.yaml        # Service schema definitions & descriptions
└── translations/        # Localization strings (en, es, etc.)
```

---

## Core Architectural Concepts

### Coordinator Pattern

The integration uses Home Assistant's `DataUpdateCoordinator` pattern:

- **`OpenEVSEUpdateCoordinator`** (in `__init__.py`): Polls the charger for all primary telemetry and sensor data. Most entity platforms are `CoordinatorEntity` subclasses that re-render upon coordinator updates.
- **`OpenEVSEFWUpdateCoordinator`** (in `__init__.py`): A dedicated coordinator checking for available firmware releases via GitHub's API on an independent schedule.

### `OpenEVSEManager`

A wrapper around the [`python-openevse-http`](https://github.com/firstof9/python-openevse-http) client library:
- Holds the active HTTP and WebSocket connection to the EVSE charger.
- Exposes charger command methods (`set_override`, `make_claim`, `set_current`, etc.).
- Exposes `version_check(min_version: str) -> bool` to gate firmware-dependent features safely.

### Real-Time WebSocket Push

In addition to polling, the integration subscribes to the charger's live WebSocket event stream. When the charger broadcasts an instantaneous state change (e.g. vehicle plugged in, relay click, amperage variation):
1. The `handle_state_change` callback updates the coordinator snapshot in memory.
2. `coordinator.async_set_updated_data()` immediately notifies subscribed entities without waiting for the next periodic poll interval.

---

## Data Flow Diagram

```text
Charger (HTTP REST + WebSockets)
        │
        ▼
  OpenEVSEManager (python-openevse-http)
        │
        ├─── Polling ──▶ OpenEVSEUpdateCoordinator ──▶ Entity state refresh
        │
        └─── WS Push ──▶ handle_state_change() ──▶ coordinator.async_set_updated_data()
                                                          └─▶ Instant entity update
```

---

## Entity Description Pattern

Entities are declared using typed `EntityDescription` dataclasses:

```python
@dataclass
class OpenEVSESensorEntityDescription(SensorEntityDescription):
    value_fn: Callable[[dict], Any] | None = None
    min_version: str | None = None
    is_async_value: bool = False
    value: str | None = None
```

All entity definitions reside as tuples of immutable descriptions in `const.py` (e.g., `SENSOR_TYPES`, `SWITCH_TYPES`, `BINARY_SENSORS`). During platform setup, `async_setup_entry` iterates through these definitions.

### Firmware Version Gating

- **Entity Platform Registration**: If `min_version` is specified on an entity description and the charger's installed firmware is lower, the entity is skipped or flagged `available = False`.
- **Services**: Handlers call `version_check()` explicitly at execution time, raising a user-friendly `HomeAssistantError` if the charger firmware does not support the action.

---

## Diagnostics & Repairs Integration

- **Diagnostics**: The integration integrates with Home Assistant's native diagnostics system. Complete non-sensitive state dumps can be downloaded from **Settings ➔ Devices & Services ➔ OpenEVSE ➔ Download Diagnostics**.
- **Repairs**: On firmware `5.1.0+`, active hardware advisories or faults automatically create manageable issues in Home Assistant's **Repairs Dashboard** (`Settings ➔ System ➔ Repairs`), allowing direct acknowledgement and remediation.
