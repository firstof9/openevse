# Entities & Platforms

The OpenEVSE integration exposes entities across **9 Home Assistant platforms**. Entities with a minimum firmware badge require that firmware version or higher to be functional; they will be skipped or marked unavailable on older firmware.

---

## Sensors (`sensor`)

| Entity Name | Key | Unit | Firmware | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Station Status** | `status` | — | Any | Overall EVSE station operational state |
| **Charging Status** | `state` | — | Any | Real-time state (`Charging`, `Connected`, `Sleeping`, etc.) |
| **Charge Time Elapsed** | `charge_time_elapsed` | min | Any | Active charging session elapsed duration (Diagnostic) |
| **Current Power Usage (Actual)** | `current_power` | W | **4.2.2+** | Hardware-measured active power draw |
| **Current Power Usage (Calculated)** | `charging_power` | W | Any | Calculated power from Volts × Amps |
| **Charging Voltage** | `charging_voltage` | V | Any | Real-time line voltage measurement |
| **Charging Current** | `charging_current` | A | Any | Real-time current delivered to the vehicle |
| **Usage this Session** | `usage_session` | kWh | Any | Energy transferred during active session (HA Energy compatible) |
| **Total Usage** | `usage_total` | kWh | Any | Lifetime cumulative energy consumption (`total_increasing`) |
| **Usage (Today)** | `total_day` | kWh | **3.0.0+** | Daily energy consumption (Disabled by default) |
| **Usage (Week)** | `total_week` | kWh | **3.0.0+** | Weekly energy consumption (Disabled by default) |
| **Usage (Month)** | `total_month` | kWh | **3.0.0+** | Monthly energy consumption (Disabled by default) |
| **Usage (Year)** | `total_year` | kWh | **3.0.0+** | Yearly energy consumption (Disabled by default) |
| **Ambient Temperature** | `ambient_temperature` | °C | Any | Temperature sensor inside the enclosure |
| **IR Temperature** | `ir_temperature` | °C | Any | Infrared temperature sensor (Disabled by default) |
| **RTC Temperature** | `rtc_temperature` | °C | Any | Real-time clock crystal temperature (Disabled by default) |
| **ESP32 Temperature** | `esp_temperature` | °C | Any | Internal ESP32 MCU core temperature (Disabled by default) |
| **WiFi Signal Strength** | `wifi_signal` | dBm | Any | Wireless signal RSSI (Diagnostic) |
| **WiFi Firmware Version** | `wifi_firmware` | — | Any | ESP module firmware version (Diagnostic) |
| **Controller Firmware** | `openevse_firmware` | — | Any | OpenEVSE core controller firmware version (Diagnostic) |
| **Protocol Version** | `protocol_version` | — | Any | Internal communications protocol (Disabled by default) |
| **Service Level** | `service_level` | — | Any | Level 1 (120V) or Level 2 (240V) service (Diagnostic) |
| **Max Amps** | `max_amps` | A | Any | Hardware electrical limit (Diagnostic) |
| **Min Amps** | `min_amps` | A | Any | Minimum pilot amperage supported (Diagnostic) |
| **Current Capacity** | `current_capacity` | A | Any | Active capacity limit (Diagnostic) |
| **Max Current** | `max_current` | A | Any | Hard ceiling configured on the charger (Diagnostic) |
| **Override State** | `override_state` | — | **4.1.0+** | Active override state flag (Diagnostic) |
| **PV Available Current** | `available_current` | A | Any | Solar excess amperage calculated (Diagnostic) |
| **PV Smoothed Available Current**| `smoothed_available_current` | A | Any | Filtered solar current (Diagnostic) |
| **PV Charge Rate** | `charge_rate` | A | Any | Target rate set by solar divert algorithm |
| **Shaper Power** | `shaper_live_power` | W | **4.1.0+** | Live household consumption read by shaper |
| **Shaper Current Available** | `shaper_available_current` | A | **4.1.0+** | Calculated amperage headroom remaining |
| **Shaper Max Power** | `shaper_max_power` | W | **4.1.0+** | Household power cap set on charger |
| **Divert Mode** | `divertmode` | — | Any | Active divert mode (`fast` or `eco`) |
| **Sensor Scale** | `ammeter_scale_factor` | — | Any | Internal calibration factor (Disabled by default) |
| **Vehicle Battery Level** | `vehicle_soc` | % | **4.1.0+** | Battery percentage pushed from external sensor |
| **Vehicle Range** | `vehicle_range` | km | **4.1.0+** | Remaining range pushed from external sensor |
| **Vehicle Charge Completion** | `vehicle_eta` | Timestamp | **4.1.0+** | ETA timestamp pushed from external sensor |
| **GFCI Trip Count** | `gfi_trip_count` | — | Any | Total lifetime ground fault trips (`total_increasing`) |
| **No Ground Trip Count** | `no_gnd_trip_count` | — | Any | Total missing ground trips (`total_increasing`) |
| **Stuck Relay Trip Count** | `stuck_relay_trip_count` | — | Any | Total stuck relay incidents (`total_increasing`) |
| **Notification Count** | `notifications_count` | — | **5.1.0+** | Active advisory notifications count |
| **Notification Severity** | `notifications_severity` | — | **5.1.0+** | Peak advisory severity (`none`, `info`, `warning`, `error`) |

---

## Binary Sensors (`binary_sensor`)

| Entity Name | Key | Device Class | Firmware | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Vehicle Connected** | `vehicle` | `plug` | Any | Detects whether cable is plugged into vehicle |
| **Manual Override** | `manual_override` | `power` | Any | Indicates active manual override |
| **Divert Active** | `divert_active` | `power` | Any | Solar divert actively regulating charge rate |
| **Shaper Active** | `shaper_active` | `power` | Any | Current shaper actively throttling charge rate |
| **Limit Active** | `has_limit` | `power` | Any | Active session limit in effect (Disabled by default) |
| **OTA Update** | `ota_update` | `update` | Any | Firmware flash actively running (Disabled by default) |
| **MQTT Connected** | `mqtt_connected` | `connectivity` | Any | Charger connection to MQTT broker (Disabled by default) |
| **Ethernet Connected** | `using_ethernet` | `connectivity` | Any | Hardware wired ethernet active (Disabled by default) |
| **Shaper Updated** | `shaper_updated` | — | Any | Shaper telemetry updated recently (Disabled by default) |
| **Vehicle Range Miles**| `mqtt_vehicle_range_miles` | — | Any | Range reported in imperial miles (Disabled by default) |

---

## Switches (`switch`)

| Entity Name | Key | Firmware | Notes |
| :--- | :--- | :--- | :--- |
| **Sleep Mode (Legacy)** | `state` | Any | Basic toggle; disabled by default |
| **Sleep Mode** | `state` | **4.1.0+** | Claim-based sleep toggle; disabled by default |
| **Manual Override** | `manual_override` | **4.1.0+** | Turn manual override on or off |
| **Solar PV Divert** | `divert_active` | **4.1.0+** | Enable or disable automated solar diversion |
| **Current Shaper** | `shaper_active` | **4.1.0+** | Enable or disable household overload throttling |
| **RFID Access** | `rfid_enabled` | **4.1.4+** | Require RFID badge authorization before charging |
| **Vehicle Range Miles**| `mqtt_vehicle_range_miles` | Any | Toggle MQTT telemetry distance unit |

---

## Buttons (`button`)

| Entity Name | Key | Firmware | Category | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Restart WiFi** | `restart_wifi` | Any | Config | Reboots the ESP WiFi / Ethernet module |
| **Restart EVSE** | `restart_evse` | Any | Config | Resets the core OpenEVSE microcontroller |
| **Learn RFID Tag** | `add_rfid_tag` | **4.0.0+** | Config | Puts reader into 15-second pairing mode |
| **Stuck-Relay Recovery** | `stuck_relay_recovery` | Controller **9.3.0+** | Diagnostic | Triggers mechanical stuck-relay unstuck pulse |
| **Reset Energy Meter** | `reset_energy_meter` | **4.0.0+** | Config | Resets session and internal energy counters |

---

## Select (`select`), Number (`number`), Light (`light`), Calendar (`calendar`), & Update (`update`)

| Platform | Entity Name | Key / Range | Firmware | Description |
| :--- | :--- | :--- | :--- | :--- |
| `number` | **Charge Rate** | `1A` – `48A` | Any | Soft limit pilot current adjustment slider |
| `select` | **Charge Rate** | `1` – `48` | Any | Discrete dropdown current limit (Disabled by default) |
| `select` | **Override State** | `active`, `auto`, `disabled` | **4.1.0+** | Direct override operational mode dropdown |
| `select` | **Divert Mode** | `fast`, `eco` | Any | Solar PV divert optimization strategy |
| `light` | **LED Brightness** | `0` – `100%` | **4.1.0+** | Front LCD backlight and LED strip brightness |
| `calendar`| **Schedule** | Calendar events | **4.0.0+** | Visual schedule management with start/stop/SoC limits |
| `update` | **OpenEVSE Update**| Firmware releases | Any | OTA firmware detection, changelog review, and installation |

---

## Home Assistant Diagnostics

The integration fully implements native Home Assistant Diagnostics. You can export a non-sensitive diagnostic dump:

**Settings ➔ Devices & Services ➔ OpenEVSE ➔ Download Diagnostics**
