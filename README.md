# OpenEVSE Integration for Home Assistant

Custom component to integrate with [OpenEVSE](https://openevse.com/) electric vehicle chargers.

<p align="center">
  <!-- Status & Release -->
  <a href="https://github.com/firstof9/openevse/releases"><img src="https://img.shields.io/github/release/firstof9/openevse.svg?style=for-the-badge" alt="GitHub Release"></a>
  <a href="https://github.com/firstof9/openevse/commits/main"><img src="https://img.shields.io/github/commit-activity/y/firstof9/openevse.svg?style=for-the-badge" alt="GitHub Activity"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/firstof9/openevse.svg?style=for-the-badge" alt="License"></a>
  <br>
  <!-- Compatibility & HACS -->
  <a href="https://github.com/custom-components/hacs"><img src="https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge" alt="HACS"></a>
  <img src="https://img.shields.io/badge/HA-2024.5+-blue.svg?style=for-the-badge" alt="Home Assistant Minimum Version">
  <img src="https://img.shields.io/badge/maintainer-Chris%20Nowak%20%40firstof9-blue.svg?style=for-the-badge" alt="Project Maintenance">
  <br>
  <!-- Community & Support -->
  <a href="https://discord.gg/Qa5fW2R"><img src="https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge&logo=discord&logoColor=white" alt="Discord"></a>
  <a href="https://community.home-assistant.io/"><img src="https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge" alt="Community Forum"></a>
  <a href="https://www.buymeacoffee.com/firstof9"><img src="https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge" alt="BuyMeCoffee"></a>
</p>

---

The **OpenEVSE** Home Assistant integration provides direct, local control over your OpenEVSE charging station. It utilizes the local API over WiFi or Ethernet to communicate, ensuring that all data remains local, secure, and fast without any cloud dependencies.

## Key Features

- ⚡ **Local Control**: Completely local communication over WiFi or Ethernet—no cloud service required.
- 🔍 **Auto-Discovery**: Automatic discovery of your charger using Zeroconf.
- 🔄 **Real-Time Data**: Fast updates via WebSockets for real-time status and power monitoring.
- 📈 **HA Energy Integration**: Out-of-the-box support for the Home Assistant Energy dashboard via dedicated session and total energy sensors.
- ☀️ **Solar PV Divert Mode**: Dynamically adjust charging current based on your home's excess solar power.
- 🛡️ **Claim & Override System**: Safely queue, override, or limit charge rates and sessions using Home Assistant services or the UI.
- 🎨 **LED Brightness Control**: Manage the charger's LED display brightness directly (firmware v4.1.0+).
- 🆙 **Firmware Updates**: Track, download, and install charger firmware updates directly within Home Assistant.

---

## Installation

### Installation via HACS (Recommended)

Click the badge below to open this repository in HACS:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=firstof9&repository=openevse&category=integration)

Alternatively, add it manually within HACS:
1. Navigate to **HACS** in your Home Assistant UI.
2. Click the three dots in the upper-right corner and select **Custom repositories**.
3. Paste the URL: `https://github.com/firstof9/openevse`
4. Select the category **Integration** and click **Add**.
5. Find the **OpenEVSE** integration in HACS and click **Install**.
6. **Restart Home Assistant** after the installation completes.

### Manual Installation (Advanced)

<details>
<summary>Click to view manual installation steps</summary>

> [!WARNING]
> Manual installation bypasses HACS updates. It is highly recommended to use HACS unless you have a specific reason to install manually.

1. Open your Home Assistant configuration directory (where you find `configuration.yaml`).
2. If it does not exist, create a folder named `custom_components`.
3. Inside `custom_components`, create a new folder named `openevse`.
4. Download the contents of the `custom_components/openevse/` directory from this repository and place them inside the new folder.
5. **Restart Home Assistant**.
</details>

---

## Configuration

### Initial Setup
1. In the Home Assistant UI, go to **Settings** -> **Devices & Services**.
2. If your OpenEVSE charger is detected automatically via Zeroconf, click **Configure** on the discovered device.
3. If not, click **+ Add Integration** in the bottom right, search for **OpenEVSE**, and select it.
4. Enter the charger's **Host/IP address** (default: `openevse.local`), and optional **Username** and **Password** if your charger requires authentication.

> [!NOTE]
> If configuring the integration to use **HTTPS / SSL**, certificate files must be uploaded to the OpenEVSE device first.


### Advanced Options (Integration Configuration)
To unlock smart features like **Solar PV Divert** and **Current Shaper**, you must bind external sensors.
1. Go to **Settings** -> **Devices & Services** -> **OpenEVSE**.
2. Click **Configure** on the OpenEVSE integration card.
3. Configure the following sensors as needed:
   - **Grid Sensor**: The sensor measuring net grid power (in Watts).
   - **Solar Sensor**: The sensor measuring solar generation power (in Watts).
   - **Voltage Sensor**: The sensor measuring grid voltage (in Volts).
   - **Shaper Sensor**: The sensor measuring live power used by other household appliances (in Watts) for overload protection.
   - **Invert Grid**: Toggle this if your grid sensor uses negative values for export.

---

## Exposed Platforms & Entities

The integration sets up the following platforms and entities:

| Platform | Key Entities | Description |
| :--- | :--- | :--- |
| `binary_sensor` | • Vehicle Connected<br>• Manual Override<br>• Divert Active<br>• Shaper Active<br>• Limit Active<br>• OTA Update<br>• MQTT Connected | Real-time binary states and diagnostics. |
| `button` | • Restart WiFi<br>• Restart EVSE | Triggers to restart hardware components. |
| `light` | • LED Brightness | Control charger screen/LED brightness (v4.1.0+). |
| `number` | • Charge Rate | Soft-limit current capacity adjustments (in Amps). |
| `select` | • Charge Rate<br>• Divert Mode (`fast` / `eco`) | Select charge limits, divert types, or override status. |
| `sensor` | • Station Status<br>• Charging Status<br>• Charging Voltage / Current<br>• Current Power Usage (Actual & Calc)<br>• Usage this Session (Energy)<br>• Total Usage (Energy)<br>• WiFi Signal Strength<br>• Temperatures (Ambient, ESP32, RTC, IR)<br>• Vehicle Battery Level (SOC) (v4.1.0+) | Sensor telemetry, stats, and diagnostic measurements. |
| `switch` | • Sleep Mode<br>• Manual Override (v4.1.0+)<br>• Solar PV Divert (v4.1.0+)<br>• Current Shaper (v4.1.0+) | Controls to toggle operational modes of the EVSE. |
| `update` | • OpenEVSE Update | Detects controller firmware updates, provides release notes, and installs updates. |

---

## Service Reference

Services are prefixed with `openevse.` (e.g., `openevse.set_override`).

### Set/Clear Overrides
* **`openevse.set_override`**: Sets a manual override on the charger.
  - Parameters:
    - `state` (optional): Set to `active` (start charging) or `disabled` (stop charging).
    - `charge_current` (optional, 1-48A): Target charge current.
    - `max_current` (optional, 1-48A): Maximum allowed current.
    - `auto_release` (optional, boolean): Automatically release override on vehicle disconnect.
* **`openevse.clear_override`**: Clears the active manual override, returning the charger to its normal programmed behavior.

### Claims Management
Claims allow multiple automations or external apps to request different charger states safely.
* **`openevse.make_claim`**: Register or update a state claim on the charger.
  - Parameters: `state`, `charge_current`, `max_current`, `auto_release`.
* **`openevse.release_claim`**: Release the current integration claim.
* **`openevse.list_claims`** *(Returns Response Data)*: Returns a dictionary of all active claims on the EVSE.

### Charge Limits
* **`openevse.set_limit`**: Set limits for the charging session.
  - Parameters:
    - `type` (required): `time` (minutes), `energy` (Wh), `soc` (%), or `range` (km/mi).
    - `value` (required, integer): Target value.
    - `auto_release` (optional, boolean): Release limit on vehicle disconnect.
* **`openevse.clear_limit`**: Clear any active session limit.
* **`openevse.get_limit`** *(Returns Response Data)*: Retrieve current session limits from the charger.
* **`openevse.list_overrides`** *(Returns Response Data)*: List active overrides on the EVSE.

### Service Call Examples

Here are some examples of how to invoke these services in your Home Assistant automations or scripts:

#### Set Manual Override
Start charging immediately at `24 Amps` and release the override once the vehicle is disconnected:
```yaml
service: openevse.set_override
target:
  entity_id: sensor.openevse_charging_status
data:
  state: active
  charge_current: 24
  auto_release: true
```

#### Set Charge Limit (SoC)
Stop charging once the vehicle's battery level reaches `80%`:
```yaml
service: openevse.set_limit
target:
  entity_id: sensor.openevse_charging_status
data:
  type: soc
  value: 80
  auto_release: true
```

#### Clear Active Limit
Remove any active time, energy, SoC, or range limit on the charger:
```yaml
service: openevse.clear_limit
target:
  entity_id: sensor.openevse_charging_status
```

---

## Dashboards & UI

For the best user experience, it is highly recommended to install the [OpenEVSE Card](https://github.com/KipK/openevse-card) via HACS (Frontend section). It is designed to match this integration perfectly.

![OpenEVSE Card Preview](https://github.com/KipK/openevse-card/raw/main/assets/card.png)

This card provides:
- Real-time charger state & power usage charts.
- Quick controls for manual overrides and sleep toggle.
- Simple slider adjustments for charge current limit.

---

## Contributions

Contributions are welcome! Please read the [Contribution Guidelines](CONTRIBUTING.md) before submitting pull requests.

If you like this integration, consider supporting the project:

<a href="https://www.buymeacoffee.com/firstof9"><img src="https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge" alt="BuyMeCoffee"></a>

---

## Roadmap

- [ ] Add Wiki
- [ ] Expand documentation
- [ ] Add Schedule Support
- [x] Add tests
- [x] Current / Voltage / Power sensors
- [x] Session & Total Energy sensors
- [x] Temperatures & Status indicators
- [x] Vehicle Connected detection
- [x] RSSI & Wifi Strength
- [x] Max & Charge Current controls
- [x] Solar PV Divert Mode
- [x] Current Shaper support
- [x] Auto-discovery (Zeroconf)
- [x] Setup and reconfiguration via UI
- [x] WebSocket Real-Time updates
- [x] Home Assistant Energy Integration
