# Scheduling & Calendar

The OpenEVSE integration exposes a **`calendar`** platform entity (`calendar.openevse_schedule`) that allows you to view, create, and manage scheduled charging events directly within Home Assistant.

::: warning Requirements
The Schedule calendar entity requires **firmware 4.0.0 or higher**. On older firmware, this entity will not be registered.
:::

---

## How It Works

OpenEVSE chargers have a built-in internal scheduler controlling when charging begins, ends, or throttles. The integration translates this schedule into a native Home Assistant `calendar` entity:

- **View upcoming windows**: Inspect scheduled charging windows in the Home Assistant Calendar view.
- **Create events**: Add scheduled charging windows through the UI or with automations.
- **Delete events**: Cancel planned windows on demand.

Each calendar event represents a discrete charging window on the charger, defined by a start time, end time, and optional charge limit (SoC percentage).

---

## Using the Calendar UI

1. Open the **Calendar** tab from the Home Assistant sidebar.
2. Select the **OpenEVSE Schedule** calendar from the list.
3. Click any existing event to view details or remove it.
4. Click on an empty time slot to schedule a new charging window.

| Event Field | Description |
| :--- | :--- |
| **Start Time** | When the charging session is authorized to start |
| **End Time** | When the charging session must stop |
| **Day of Week** | Single occurrence or recurring weekly window |
| **SoC Limit** | Optional: Stop charging when vehicle battery reaches this percentage |

---

## Automations & Service Calls

### Creating Events via Automations

Use the standard Home Assistant `calendar.create_event` action:

```yaml
action: calendar.create_event
target:
  entity_id: calendar.openevse_schedule
data:
  summary: "Off-Peak Overnight Charge"
  start_date_time: "2026-10-15T23:00:00"
  end_date_time: "2026-10-16T06:00:00"
```

::: tip Timezone Accuracy
The schedule calendar uses local time from your Home Assistant configuration. Ensure your charger's clock and timezone match using `openevse.set_time` or NTP synchronization (`openevse.sync_time`).
:::

### Deleting Events via Automations

```yaml
action: calendar.delete_event
target:
  entity_id: calendar.openevse_schedule
data:
  uid: "<event-uid>"
```

---

## Key Notes & Behavior

- **Weekly Recurrence**: Recurring events map to weekly repeating schedules stored in the charger's flash memory.
- **Immediate Effect**: Schedule edits apply to the charger immediately without rebooting.
- **Two-Way Synchronization**: If you modify schedules through the OpenEVSE web interface directly, the Home Assistant calendar entity automatically reflects those adjustments at the next coordinator poll.
