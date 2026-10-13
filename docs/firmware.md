# Firmware Updates

The OpenEVSE integration includes a native **`update`** platform entity (`update.openevse_update`) that hooks directly into Home Assistant's update infrastructure for one-click Over-The-Air (OTA) firmware management.

---

## How It Works

The **OpenEVSE Update** entity:
- Queries GitHub Releases for new official OpenEVSE WiFi firmware releases.
- Displays the **currently installed version** against the **latest available release**.
- Renders the official **release notes and changelog** right inside the update card.
- Provides a one-click **Install** button to trigger the OTA upgrade sequence on the charger.

Find it under: **Settings ➔ Devices & Services ➔ OpenEVSE ➔ (Device) ➔ Update**.

::: warning Keep Power Connected
Do not unplug power to the charger during an OTA firmware flash. The charger will automatically reboot and reconnect to WiFi upon completion.
:::

---

## GitHub API Rate Limiting & Access Tokens

By default, anonymous queries to GitHub's public API are limited to **60 requests per hour** per external IP address. While usually adequate, shared public IPs or multiple containers can encounter temporary rate limits.

### How to Add a GitHub Personal Access Token

1. Generate a token on GitHub: **GitHub ➔ Settings ➔ Developer settings ➔ Personal access tokens (classic)**.
2. No specific permissions/scopes are needed (public repository data is freely accessible with a basic token).
3. In Home Assistant, open **Settings ➔ Devices & Services ➔ OpenEVSE ➔ Configure**.
4. Paste the token into the **GitHub Personal Access Token** field and submit.

This instantly upgrades your rate limit ceiling from 60 to **5,000 requests per hour**.

---

## Firmware Version Capability Matrix

OpenEVSE WiFi firmware `2.x+` is supported. Use this capability matrix to check which firmware version unlocks specific features:

| Firmware Version | Features Unlocked |
| :--- | :--- |
| **2.x+** | Core telemetry (voltage, current, power, energy, temperatures, WiFi signal strength), basic overrides |
| **3.0.0+** | Periodic energy statistics (Daily, Weekly, Monthly, Yearly sensors) |
| **4.0.0+** | RFID pairing (`Learn RFID Tag`), Schedule Calendar, Reset Energy Meter, TLS/SSL and Root CA installation |
| **4.1.0+** | Manual Override switch, Solar PV Divert switch, Current Shaper switch, LED brightness control, vehicle SoC / range / ETA push, Shaper diagnostics |
| **4.1.4+** | RFID Access security toggle switch |
| **4.2.2+** | Live Actual Current Power Usage sensor (`current_power`) |
| **5.0.0+** | RFID user assignments (`set_rfid_user`, `delete_rfid_user`, `get_rfid_users`) |
| **5.1.0+** | Advisory notifications sensors (`notifications_count`, `notifications_severity`), advisory services (`get_notifications`, `acknowledge_notification`), and Home Assistant Repairs integration |
| **Controller 9.3.0+** | Stuck-Relay Recovery button |

---

## Manual Firmware Refresh

To trigger an on-demand check for new firmware versions without waiting for the coordinator interval:

```yaml
action: homeassistant.update_entity
target:
  entity_id: update.openevse_update
```
