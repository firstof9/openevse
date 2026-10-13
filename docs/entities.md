# Platforms & Entities

The OpenEVSE integration automatically registers a wide range of entity platforms depending on your charger's hardware modules and firmware version.

---

## Entity Summary Table

| Platform | Key Entities | Type / Range | Description |
| :--- | :--- | :--- | :--- |
| `sensor` | `sensor.openevse_charging_status` | State string | Current state (e.g., `Charging`, `Connected`, `Sleeping`, `Disabled`). |
| `sensor` | `sensor.openevse_station_status` | State string | EVSE state string (e.g., `Active`, `Disabled`). |
| `sensor` | `sensor.openevse_charging_voltage` | `V` (Volts) | Live AC voltage measurement. |
| `sensor` | `sensor.openevse_charging_current` | `A` (Amps) | Real-time current delivered to vehicle. |
| `sensor` | `sensor.openevse_power_usage` | `W` (Watts) | Active power draw. |
| `sensor` | `sensor.openevse_usage_this_session`| `kWh` | Energy consumed in the active session. |
| `sensor` | `sensor.openevse_total_usage` | `kWh` | Lifetime cumulative energy consumption (Energy Dashboard compatible). |
| `sensor` | `sensor.openevse_wifi_signal_strength`| `dBm` / `%` | WiFi RSSI and connection quality. |
| `sensor` | `sensor.openevse_ambient_temperature` | `°C` / `°F` | Sensor temperature inside enclosure. |
| `sensor` | `sensor.openevse_vehicle_soc` | `%` | Vehicle battery percentage (firmware v4.1.0+). |
| `binary_sensor` | `binary_sensor.openevse_vehicle_connected` | `on` / `off` | Detects when EV charging cable is plugged into vehicle. |
| `binary_sensor` | `binary_sensor.openevse_manual_override` | `on` / `off` | Indicates if an active manual override is applied. |
| `binary_sensor` | `binary_sensor.openevse_divert_active` | `on` / `off` | Indicates solar PV divert is controlling charge rate. |
| `binary_sensor` | `binary_sensor.openevse_shaper_active` | `on` / `off` | Indicates grid current shaper is throttling current. |
| `binary_sensor` | `binary_sensor.openevse_ota_update` | `on` / `off` | Shows whether firmware is currently flashing. |
| `binary_sensor` | `binary_sensor.openevse_mqtt_connected` | `on` / `off` | EVSE MQTT broker connection status. |
| `switch` | `switch.openevse_sleep_mode` | `on` / `off` | Put charger to sleep or resume active state. |
| `switch` | `switch.openevse_manual_override` | `on` / `off` | Toggle manual override mode directly. |
| `switch` | `switch.openevse_solar_pv_divert` | `on` / `off` | Toggle automated solar diversion. |
| `switch` | `switch.openevse_current_shaper` | `on` / `off` | Toggle home overload current shaping. |
| `switch` | `switch.openevse_rfid_access` | `on` / `off` | Require RFID card authentication before charging. |
| `number` | `number.openevse_charge_rate` | `6A` – `48A` | Adjust pilot charge current soft limit. |
| `select` | `select.openevse_divert_mode` | `fast`, `eco` | Select solar PV divert algorithm mode. |
| `light` | `light.openevse_led_brightness` | `0` – `100%` | Adjust LCD / LED backlight brightness. |
| `button` | `button.openevse_restart_wifi` | Trigger | Reboot the ESP WiFi / Ethernet module. |
| `button` | `button.openevse_restart_evse` | Trigger | Reset the OpenEVSE controller board. |
| `button` | `button.openevse_learn_rfid_tag` | Trigger | Trigger RFID card enrollment mode. |
| `calendar` | `calendar.openevse_schedule` | Calendar events | View and configure scheduled charge sessions. |
| `update` | `update.openevse_update` | Firmware state | Firmware tracking and one-click upgrades. |
