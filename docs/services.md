# Service Calls Reference

The OpenEVSE integration registers several custom Home Assistant services prefixed with `openevse.`.

You can use these services in Home Assistant automations, scripts, or from Developer Tools ➔ Actions/Services.

---

## Overrides

### `openevse.set_override`
Sets a manual override on the charger to immediately activate or disable charging with optional current constraints.

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `state` | string | No | `active` (force start charging) or `disabled` (stop charging). |
| `charge_current` | integer | No | Desired charge current limit in Amps (`1` – `48`). |
| `max_current` | integer | No | Maximum current cap in Amps (`1` – `48`). |
| `auto_release` | boolean | No | If `true`, the override is automatically cleared when the car is disconnected. |

#### YAML Example
```yaml
action: openevse.set_override
target:
  entity_id: sensor.openevse_charging_status
data:
  state: active
  charge_current: 32
  auto_release: true
```

### `openevse.clear_override`
Clears the active manual override, allowing the charger to revert to its scheduled or default mode.

```yaml
action: openevse.clear_override
target:
  entity_id: sensor.openevse_charging_status
```

---

## Limits

### `openevse.set_limit`
Sets a session limit on the charger (energy, time, SoC, or range).

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `type` | string | Yes | Limit type: `time` (minutes), `energy` (Wh), `soc` (%), or `range` (km/mi). |
| `value` | integer | Yes | Target numerical value for the limit. |
| `auto_release` | boolean | No | Automatically remove limit once disconnected. |

#### Example (Charge to 80% State of Charge)
```yaml
action: openevse.set_limit
target:
  entity_id: sensor.openevse_charging_status
data:
  type: soc
  value: 80
  auto_release: true
```

### `openevse.clear_limit`
Removes any active session limit.

```yaml
action: openevse.clear_limit
target:
  entity_id: sensor.openevse_charging_status
```

### `openevse.get_limit` *(Returns Response)*
Fetches active limit information from the charger in response data.

---

## Claims Management

Claims allow external systems to safely prioritize and coordinate charger control.

### `openevse.make_claim`
Creates or updates a claim with parameters `state`, `charge_current`, `max_current`, and `auto_release`.

### `openevse.release_claim`
Releases the current claim made by the integration.

### `openevse.list_claims` *(Returns Response)*
Returns a JSON structure listing all claims currently active on the OpenEVSE hardware.

---

## Time & NTP Synchronization

### `openevse.sync_time`
Forces the charger to perform an immediate network time synchronization via NTP.

```yaml
action: openevse.sync_time
target:
  entity_id: sensor.openevse_charging_status
```

### `openevse.set_time`
Manually sets clock, timezone string, or toggles SNTP client.

---

## RFID Management

### `openevse.add_rfid_tag`
Puts the charger into RFID learning mode to scan and register the next card/tag presented (v4.0.0+).

```yaml
action: openevse.add_rfid_tag
target:
  entity_id: sensor.openevse_charging_status
```

### `openevse.set_rfid_user`
Maps an RFID card ID to a Home Assistant person entity or friendly user name (v5.0.0+).

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `rfid` | string | Yes | Card UID string (e.g., `01020304`). |
| `person` | string | No | Home Assistant person entity ID (e.g. `person.jane_doe`). |
| `name` | string | No | Friendly human-readable name. |

```yaml
action: openevse.set_rfid_user
target:
  entity_id: sensor.openevse_charging_status
data:
  rfid: "3A4B5C6D"
  name: "Jane Doe"
```

### `openevse.delete_rfid_user`
Removes an RFID tag assignment from the charger.

### `openevse.get_rfid_users` *(Returns Response)*
Retrieves all enrolled RFID cards and their mapped users from the EVSE.
