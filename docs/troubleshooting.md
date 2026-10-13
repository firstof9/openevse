# Troubleshooting & FAQ

Frequently asked questions and troubleshooting advice for the OpenEVSE Home Assistant integration.

---

## Frequently Asked Questions

### Can I run this integration completely offline?
**Yes.** All communication occurs on your local network (LAN) directly with the OpenEVSE controller over HTTP REST and WebSockets. No cloud connection or internet access is necessary for charger management.

### Why does Solar Divert not start immediately when surplus solar is generated?
To prevent damaging the vehicle's onboard charger or cycling contactors excessively:
- The integration requires a sustained period of excess solar above the minimum charge threshold (typically 6A / ~1.4 kW single-phase or ~4.1 kW three-phase).
- Smoothing windows and hysteresis prevent frequent cycling during cloudy spells.

### How do I configure HTTPS / TLS?
If your OpenEVSE firmware has SSL enabled, configure the integration with port `443` and ensure that certificates are uploaded to the OpenEVSE device.

---

## Troubleshooting Guide

### 1. Device Not Found via Auto-Discovery
- **VLAN Isolation**: Ensure multicast DNS (mDNS / Zeroconf) packets can traverse across your IoT VLAN and your Home Assistant VLAN.
- **Manual Setup**: If mDNS is disabled, manually add the integration via **Settings ➔ Devices & Services ➔ + Add Integration ➔ OpenEVSE** and specify the charger's static IP address.

### 2. WebSocket Disconnections or Stale Data
- Verify the WiFi signal quality using `sensor.openevse_wifi_signal_strength`.
- Check if another application (e.g. an external script) is exhausting WebSocket connections on the ESP module. OpenEVSE ESP firmware supports a limited number of concurrent WebSocket clients.

### 3. Firmware Update Fails
- Ensure your charger has access to the internet to download the firmware binary from GitHub releases.
- Alternatively, you can upload the `.bin` firmware file directly via the OpenEVSE web GUI.

### 4. Enable Diagnostic Debug Logging
If you need to report an issue, enable debug logging in Home Assistant:

Add the following to your `configuration.yaml`:
```yaml
logger:
  default: warning
  logs:
    custom_components.openevse: debug
    openevse_http: debug
```
Or click the **three dots** on the OpenEVSE integration card in Home Assistant and select **Enable debug logging**.
