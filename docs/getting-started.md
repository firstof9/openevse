# Getting Started

Welcome to the **OpenEVSE Home Assistant Integration** documentation!

The OpenEVSE integration provides seamless, local integration between your Home Assistant installation and [OpenEVSE](https://openevse.com/) EV charging hardware running OpenEVSE WiFi firmware (ESP8266 or ESP32).

---

## Why OpenEVSE + Home Assistant?

- **100% Local**: No proprietary cloud, subscriptions, or outside dependencies. All communication occurs directly on your home LAN via HTTP REST and WebSockets.
- **Fast Telemetry**: State updates, power draw, voltage, and session stats reflect in Home Assistant instantly.
- **Intelligent Solar Tracking**: Divert surplus rooftop solar into your electric vehicle with configurable smoothing and safety margins.
- **Home Assistant Native**: Integrates cleanly into the Home Assistant Energy dashboard, Automation Editor, and Lovelace UI.

---

## Compatibility Requirements

- **Home Assistant**: Version `2024.5` or later.
- **OpenEVSE Firmware**:
  - OpenEVSE WiFi firmware `v2.x`, `v3.x`, `v4.x`, or `v5.x` (ESP32 recommended).
  - Certain features require specific firmware versions:
    - **RFID Tag Management**: Firmware `v4.0.0+` (learning) and `v5.0.0+` (user mapping).
    - **Screen/LED Brightness Control**: Firmware `v4.1.0+`.
    - **Current Shaper & Solar Divert Controls**: Firmware `v4.1.0+`.
    - **Schedules**: Firmware `v4.0.0+`.

---

## Next Steps

1. Follow the [Installation Guide](./installation.md) to install via HACS or manually.
2. Review the [Configuration Guide](./configuration.md) to connect your charger and setup sensors.
3. Explore the [Features & Capabilities](./features.md) and [Services Reference](./services.md).
