# Troubleshooting & FAQ

Frequently asked questions, common setup scenarios, and troubleshooting steps for the OpenEVSE Home Assistant integration.

---

## Setup & Connectivity

### Integration is not discovered automatically
- **VLAN Isolation**: Zeroconf / mDNS discovery relies on multicast UDP packets which cannot traverse separated VLANs without an mDNS gateway or repeater (e.g. Avahi).
- **Manual Setup**: If discovery fails, click **+ Add Integration ➔ OpenEVSE** and manually input the charger's static IP address or local hostname.
- Verify the charger's WiFi LED is solid (not pulsing or disconnected).

### "Unable to connect to device" during initial setup
- Verify you can open `http://<CHARGER_IP>` in a browser from the same network.
- If HTTP authentication is configured on the charger, double-check your username and password.
- If using **HTTPS**, verify that SSL certificates have been provisioned on the charger.

### Integration configured but entities missing
- Ensure the charger's entry in **Settings ➔ Devices & Services ➔ OpenEVSE** shows a connected device.
- Review logs under **Settings ➔ System ➔ Logs** filtered by `openevse`.

---

## Entities & Sensors

### Why do some entities show as "Unavailable"?
Entities with a firmware version requirement (such as LED Brightness, Solar Divert, RFID Access, or Vehicle Telemetry) will report as **Unavailable** if the OpenEVSE controller or WiFi module is running older firmware.
- Check the **Controller Firmware** sensor (`sensor.openevse_controller_firmware`) and compare it with the [Firmware Capability Matrix](./firmware.md#firmware-version-capability-matrix).

### Sensor shows "Unknown" or "None"
- Certain diagnostic sensors (like solar divert or current shaper calculations) only calculate numbers when the corresponding feature switch is enabled.
- Wait for the next coordinator poll or restart the charger's WiFi if communication has frozen.

### Update entity not finding new firmware
- Anonymous GitHub API requests are capped at 60/hour. Add a [GitHub Personal Access Token](./configuration.md#additional-settings) to increase your limit to 5,000/hour.
- Manually trigger an update check using the `homeassistant.update_entity` action targeting `update.openevse_update`.

---

## Services & Automation

### Firmware version error on service call
Services like `set_rfid_user`, `delete_rfid_user`, `get_rfid_users`, or `reset_energy_meter` require modern firmware. The integration will log an informative warning if invoked on older firmware.

### `set_limit` with `soc` or `range` has no effect
These limit modes require vehicle telemetry. You must configure the **Vehicle State of Charge Sensor** or **Vehicle Range Sensor** under **Settings ➔ Devices & Services ➔ OpenEVSE ➔ Configure**.

### Manual override not taking effect
Check if another entity or external service has registered a higher-priority claim using `openevse.list_claims`.

---

## Solar Divert & Current Shaper

### Solar Divert enabled but charge current does not adjust
- Verify that your **Grid Sensor** or **Solar Sensor** is updating actively in Home Assistant. The integration transmits sensor updates reactively when state events fire.
- Verify whether your grid sensor exports power with negative numbers. If your meter reports export as positive values, enable **Invert Grid** in integration options.
- Confirm the charger has adequate current headroom above its configured **Min Amps** threshold (typically 6A).

---

## Advisory Notifications & Home Assistant Repairs

Firmware **5.1.0+** introduces hardware and operational advisories on the charger. The integration integrates with Home Assistant's native Repairs framework:

- **Automatic Repair Issues**: When an advisory or alert is raised, an issue is created in **Settings ➔ System ➔ Repairs**.
- **Acknowledgement**: You can review and acknowledge (mute) the advisory straight from the Repairs UI, or invoke `openevse.acknowledge_notification`.
- **Monitoring**: Track active advisories with `sensor.openevse_notification_count` and `sensor.openevse_notification_severity`.

---

## Diagnostic Logging

To capture deep debug logs for troubleshooting or filing an issue report:

1. In Home Assistant, click the **three dots** on the OpenEVSE card under **Settings ➔ Devices & Services** and select **Enable debug logging**.
2. Perform the action causing the issue.
3. Select **Disable debug logging** to download the resulting log file.

Alternatively, add the following to `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.openevse: debug
    openevse_http: debug
```

---

## Filing an Issue Report

When opening an issue on GitHub, please include:
1. Integration version (e.g. from HACS or release tag).
2. Home Assistant core version.
3. OpenEVSE WiFi and Controller firmware versions.
4. Debug log excerpts.
5. Non-sensitive diagnostics download (**Settings ➔ Devices & Services ➔ OpenEVSE ➔ Download Diagnostics**).
