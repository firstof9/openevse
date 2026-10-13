# Lovelace UI & Dashboards

Integrate your OpenEVSE charger into beautiful Home Assistant dashboards.

---

## Recommended: OpenEVSE Card

For the cleanest visual experience, install the dedicated custom frontend card created by **@KipK**:

- **Repository**: [OpenEVSE Card on GitHub](https://github.com/KipK/openevse-card)
- **HACS**: Available under **HACS ➔ Frontend ➔ OpenEVSE Card**.

![OpenEVSE Card Preview](https://github.com/KipK/openevse-card/raw/main/assets/card.png)

### Key Features of OpenEVSE Card
- Live dynamic status indicator (Charging, Sleeping, Disconnected, Error).
- Interactive charge current slider with real-time amperage updates.
- One-click override, sleep mode, and manual mode buttons.
- Real-time power draw graphs and session energy statistics.

---

## Custom Dashboard Example (Standard Lovelace Cards)

If you prefer standard Lovelace cards, you can build an effective dashboard with `entities`, `gauge`, and `tile` cards:

```yaml
type: vertical-stack
cards:
  - type: tile
    entity: sensor.openevse_charging_status
    name: EV Charger Status
    icon: mdi:ev-station
    color: green

  - type: gauge
    entity: sensor.openevse_power_usage
    name: Current Power Draw
    unit: W
    min: 0
    max: 9600
    needle: true
    severity:
      green: 0
      yellow: 4000
      red: 8000

  - type: entities
    title: OpenEVSE Controls
    entities:
      - entity: number.openevse_charge_rate
      - entity: switch.openevse_sleep_mode
      - entity: switch.openevse_solar_pv_divert
      - entity: binary_sensor.openevse_vehicle_connected
      - entity: sensor.openevse_usage_this_session
      - entity: sensor.openevse_total_usage
```
