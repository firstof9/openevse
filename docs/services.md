# Service Calls Reference

All integration actions are prefixed with `openevse.` (e.g. `openevse.set_override`).

Services can target **any entity** associated with an OpenEVSE charger entry (such as `sensor.openevse_charging_status`), or target the **Device ID** directly.

> [!NOTE]
> The examples below use Home Assistant's modern `action:` syntax. The legacy `service:` keyword remains fully compatible with existing automations and scripts.

---

## Overrides

Manual overrides grant immediate, priority control over charging state and current.

### `openevse.set_override`

Sets a manual override on the charger.

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `state` | string (`active` / `disabled`) | No | `active` (force start charging) or `disabled` (stop charging). |
| `charge_current` | integer (1–48) | No | Target charge current in Amps. |
| `max_current` | integer (1–48) | No | Hard current cap while allowing claims below this limit. |
| `energy_limit` | integer | No | Stop after transferring this many Wh *(reserved)*. |
| `time_limit` | integer | No | Stop after this many seconds of charging *(reserved)*. |
| `auto_release` | boolean | No | Automatically clear override when vehicle disconnects (default: `true`). |

#### Start charging immediately at 24 Amps:
```yaml
action: openevse.set_override
target:
  entity_id: sensor.openevse_charging_status
data:
  state: active
  charge_current: 24
  auto_release: true
```

#### Stop charging immediately:
```yaml
action: openevse.set_override
target:
  entity_id: sensor.openevse_charging_status
data:
  state: disabled
```

### `openevse.clear_override`

Clears the manual override, returning the EVSE to its normal automated/scheduled behavior.

```yaml
action: openevse.clear_override
target:
  entity_id: sensor.openevse_charging_status
```

### `openevse.list_overrides` *(Returns Response Data)*

Returns a list of all active overrides on the charger.

```yaml
action: openevse.list_overrides
target:
  entity_id: sensor.openevse_charging_status
response_variable: overrides
```

---

## Claims Management

Claims allow multiple independent automations, apps, or services to coordinate charger state safely without race conditions. Conflicts are resolved according to claim priority.

### `openevse.make_claim`

Register or update an active claim on the charger.

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `state` | string (`active` / `disabled`) | No | Requested operational state. |
| `charge_current` | integer (1–48) | No | Desired charging current in Amps. |
| `max_current` | integer (1–48) | No | Maximum allowable current. |
| `auto_release` | boolean | No | Automatically release claim when car unplugged. |

```yaml
action: openevse.make_claim
target:
  entity_id: sensor.openevse_charging_status
data:
  state: active
  charge_current: 16
  auto_release: true
```

### `openevse.release_claim`

Releases the integration's active claim, permitting lower-priority claims or schedules to take effect.

```yaml
action: openevse.release_claim
target:
  entity_id: sensor.openevse_charging_status
```

### `openevse.list_claims` *(Returns Response Data)*

Returns a dictionary of all active claims registered on the EVSE.

```yaml
action: openevse.list_claims
target:
  entity_id: sensor.openevse_charging_status
response_variable: claims
```

---

## Charge Limits

Set automated session stop conditions by battery percentage, energy, time, or driving range.

### `openevse.set_limit`

Sets an active limit for the current charging session.

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `type` | string | **Yes** | `soc` (%), `energy` (Wh), `time` (minutes), or `range` (km/mi). |
| `value` | integer | **Yes** | Target numerical value for the chosen limit type. |
| `auto_release` | boolean | No | Clear limit upon vehicle disconnect (default: `true`). |

#### Stop at 80% State of Charge (SoC):
```yaml
action: openevse.set_limit
target:
  entity_id: sensor.openevse_charging_status
data:
  type: soc
  value: 80
  auto_release: true
```

#### Limit session to 12.5 kWh (12,500 Wh):
```yaml
action: openevse.set_limit
target:
  entity_id: sensor.openevse_charging_status
data:
  type: energy
  value: 12500
```

### `openevse.clear_limit`

Removes any active session limit.

```yaml
action: openevse.clear_limit
target:
  entity_id: sensor.openevse_charging_status
```

### `openevse.get_limit` *(Returns Response Data)*

Retrieves the currently active session limit from the charger.

```yaml
action: openevse.get_limit
target:
  entity_id: sensor.openevse_charging_status
response_variable: limit
```

---

## Time & NTP Synchronization

### `openevse.get_time` *(Returns Response Data)*

Retrieves the date, clock time, timezone string, and SNTP sync status from the charger.

```yaml
action: openevse.get_time
target:
  entity_id: sensor.openevse_charging_status
response_variable: charger_clock
```

### `openevse.set_time`

Sets charger clock time, POSIX timezone, or configures NTP synchronization.

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `time` | string | No | ISO-8601 datetime (e.g. `2026-03-25T15:30:00Z`). |
| `timezone` | string | No | POSIX timezone or location (e.g. `America/New_York\|EST5EDT,M3.2.0,M11.1.0` or `Europe/London`). |
| `sntp` | boolean | No | Enable or disable network time sync. |

### `openevse.sync_time`

Forces the charger to perform an immediate network NTP time synchronization.

```yaml
action: openevse.sync_time
target:
  entity_id: sensor.openevse_charging_status
```

---

## RFID Management

### `openevse.add_rfid_tag` *(Firmware 4.0.0+)*
Enters RFID pairing mode to scan and register the next physical card.

```yaml
action: openevse.add_rfid_tag
target:
  entity_id: sensor.openevse_charging_status
```

### `openevse.set_rfid_user` *(Firmware 5.0.0+)*
Associates an RFID tag ID with a Home Assistant `person` entity or friendly name.

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `rfid` | string | **Yes** | RFID card UID (e.g. `01020304`). |
| `person` | entity_id | No | Home Assistant person entity ID (e.g. `person.john_doe`). |
| `name` | string | No | Friendly name text string. |

```yaml
action: openevse.set_rfid_user
target:
  entity_id: sensor.openevse_charging_status
data:
  rfid: "01020304"
  person: person.john_doe
```

### `openevse.delete_rfid_user` *(Firmware 5.0.0+)*
Deletes an RFID tag from the charger's database.

### `openevse.get_rfid_users` *(Firmware 5.0.0+)* *(Returns Response Data)*
Fetches all enrolled RFID tags and their user mappings.

---

## Energy Meter & Hardware Maintenance

### `openevse.reset_energy_meter` *(Firmware 4.0.0+)*
Resets the energy meter counters on the EVSE.

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `hard` | boolean | No | Perform a hard reset instead of soft reset (default: `false`). |
| `import` | boolean | No | Reset import energy counters (default: `false`). |

```yaml
action: openevse.reset_energy_meter
target:
  entity_id: sensor.openevse_charging_status
data:
  hard: false
  import: false
```

---

## Advisory Notifications *(Firmware 5.1.0+)*

### `openevse.get_notifications` *(Returns Response Data)*
Retrieves active advisory notices from the charger.

```yaml
action: openevse.get_notifications
target:
  entity_id: sensor.openevse_charging_status
response_variable: notifications
```

### `openevse.acknowledge_notification`
Acknowledges (mutes) an active advisory notice.

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `notification_id` | string | **Yes** | Identifier of the notification to acknowledge. |

```yaml
action: openevse.acknowledge_notification
target:
  entity_id: sensor.openevse_charging_status
data:
  notification_id: "0"
```

---

## Targeting by Device ID

In blueprints or generic automations, you can target the `device_id` directly:

```yaml
action: openevse.set_override
target:
  device_id: 38f4201b10a9c3e9821a719dbd3910f2
data:
  state: active
  charge_current: 32
```
