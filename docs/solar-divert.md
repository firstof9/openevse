# Solar PV Divert & Current Shaper

OpenEVSE includes two intelligent charging features to optimize household power distribution and maximize solar energy utilization: **Solar PV Divert** and **Current Shaper** (both require firmware **4.1.0+**).

---

## Solar PV Divert

Solar PV Divert automatically throttles charging current in real-time according to **excess solar generation**. Instead of buying peak electricity from the utility, your EV batteries store energy that would otherwise be exported.

### How it Works
1. You configure external power sensors in Home Assistant (Grid, Solar, or Voltage).
2. The integration sends updated sensor readings to the charger whenever state values change.
3. The charger's internal algorithm computes available excess current and adjusts pilot amperage.
4. If solar generation drops, charging dials back or pauses; when the sun returns, charging safely resumes.

### Divert Modes
- **`eco` Mode**: Smoothly ramps charging current up and down to match available solar. Will pause charging if solar export drops below minimum charger current (6A).
- **`fast` Mode**: Charges at the maximum configured amperage while solar excess is present; stops when excess solar ends.

### Setting Up Solar Divert

**Step 1: Configure External Sensors**
Navigate to **Settings ➔ Devices & Services ➔ OpenEVSE ➔ Configure**:
- **Grid Sensor**: Sensor measuring net grid power in Watts (`W`). Positive represents import from the grid, negative represents solar export. If your meter uses positive numbers for export, toggle **Invert Grid**.
- **Solar Sensor** *(optional)*: Dedicated rooftop solar generation sensor in Watts (`W`).
- **Voltage Sensor** *(optional)*: Real-time AC voltage sensor in Volts (`V`) for maximum calculation precision.

**Step 2: Turn on Solar PV Divert**
Toggle the **Solar PV Divert** switch (`switch.openevse_solar_pv_divert`) or invoke:

```yaml
action: switch.turn_on
target:
  entity_id: switch.openevse_solar_pv_divert
```

**Step 3: Select Divert Mode**
Select `eco` or `fast` using `select.openevse_divert_mode`.

---

## Current Shaper (Overload Protection)

The **Current Shaper** actively prevents your home electrical service from tripping main breakers or fuses. It dynamically reduces EV charging draw whenever large household appliances (heat pumps, ovens, electric dryers) push total consumption close to electrical capacity.

### How it Works
1. You provide a **Shaper Sensor** that measures live whole-home electrical consumption in Watts (`W`).
2. The integration streams live power numbers to the EVSE.
3. The charger computes real-time available headroom and safely curtails pilot current before circuit breakers overload.

### Setting Up Current Shaper

**Step 1: Select Shaper Sensor**
Go to **Settings ➔ Devices & Services ➔ OpenEVSE ➔ Configure** and pick your live whole-home consumption sensor under **Shaper Sensor**.

**Step 2: Enable Current Shaper**
Toggle the **Current Shaper** switch (`switch.openevse_current_shaper`):

```yaml
action: switch.turn_on
target:
  entity_id: switch.openevse_current_shaper
```

---

## Diagnostic & Telemetry Sensors

When Solar Divert or Current Shaper are active, additional diagnostic sensors provide real-time visibility into internal calculations (disabled by default in the Home Assistant Entity Registry):

| Sensor | Key | Units | Description |
| :--- | :--- | :--- | :--- |
| **PV Available Current** | `available_current` | A | Raw available solar current |
| **PV Smoothed Current** | `smoothed_available_current` | A | Filtered/smoothed solar current |
| **PV Charge Rate** | `charge_rate` | A | Target rate calculated by divert logic |
| **Shaper Power** | `shaper_live_power` | W | Live home power read by shaper |
| **Shaper Current Available**| `shaper_available_current` | A | Headroom available under main limit |
| **Shaper Max Power** | `shaper_max_power` | W | Maximum total power cap set on charger |
| **Divert Active** | `divert_active` | — | Binary indicator when solar divert is regulating |
| **Shaper Active** | `shaper_active` | — | Binary indicator when shaper is actively throttling |

---

## Combining Solar Divert with Session Limits

You can combine Solar Divert with battery or energy limits:

```yaml
# Divert solar power until battery reaches 80% State of Charge
action: openevse.set_limit
target:
  entity_id: sensor.openevse_charging_status
data:
  type: soc
  value: 80
  auto_release: true
```
