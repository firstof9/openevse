# Features & Capabilities

The OpenEVSE integration offers deep control over your EV charging sessions, integrating seamlessly with Home Assistant automations and energy tracking.

---

## Solar PV Divert Mode

If you have rooftop solar panels, you can channel clean, excess electricity straight into your EV rather than exporting it back to the grid.

### How it Works
1. When configured with a **Solar Sensor** and **Grid Sensor**, the integration continuously monitors net energy flow.
2. When excess generation surpasses the charger's minimum charging threshold (typically 6A), charging commences automatically.
3. If solar generation drops or household appliances cycle on, charge current dynamically adjusts downwards or pauses safely.

### Modes
- **Eco Mode**: Only charges when excess solar power is available, minimizing or eliminating grid draw.
- **Fast Mode**: Always charges at the configured rate, blending grid power and solar power as available.

You can toggle Solar Divert easily via the `switch.openevse_solar_pv_divert` entity or change modes using `select.openevse_divert_mode`.

---

## Claim and Override System

OpenEVSE firmware implements a robust **State Claim** architecture. This avoids conflicting instructions when multiple systems (schedules, solar diverts, Home Assistant automations, or user manual buttons) attempt to adjust the charger simultaneously.

- **Manual Override**: Allows you to force charging to start or stop immediately at a desired amperage.
- **Auto Release**: When set, overrides automatically terminate once the vehicle is unplugged, resetting the charger to its scheduled state for the next vehicle connection.
- **Claims Inspection**: Use `openevse.list_claims` to see active commands from other sources (e.g. MQTT, internal timers, or solar diverters).

---

## RFID Management (v4.0+ / v5.0+)

Control who can charge and correlate charging sessions with specific users:

- **Add / Learn RFID Tags**: Put the EVSE into scanning mode using the `button.openevse_learn_rfid_tag` or `openevse.add_rfid_tag` service call. Scan a physical badge or card near the reader to register it.
- **User Association**: Link an RFID tag with a Home Assistant person entity or friendly user name (`openevse.set_rfid_user`).
- **Access Control**: Enable or disable RFID authorization requirements using `switch.openevse_rfid_access`.

---

## Home Assistant Energy Dashboard

OpenEVSE entities conform to Home Assistant Energy Dashboard requirements:

- **Session Energy**: Tracks cumulative kilowatt-hours (`kWh`) for the active or most recent session.
- **Total Energy**: Monotonically increasing lifetime energy (`kWh`) with `state_class: total_increasing` and `device_class: energy`.

Simply navigate to **Settings ➔ Dashboards ➔ Energy** and select the OpenEVSE total energy sensor under **Individual devices**.

---

## Current Shaper (Overload Protection)

Protect your main home panel from tripping:
- By specifying a **Shaper Sensor** in integration options, the charger can throttle EV charge current whenever whole-home consumption nears electrical service capacity.
- As other heavy loads (heat pumps, ovens, dryers) power down, charging current safely steps back up.

---

## Firmware Updates

Never fall behind on OpenEVSE controller firmware:
- An `update.openevse_update` entity automatically checks for official GitHub releases.
- Release notes, upgrade status, and direct one-click installation are exposed right inside Home Assistant.
