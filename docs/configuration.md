# Configuration

Once the OpenEVSE integration is installed and Home Assistant has restarted, you can configure your charger via the Home Assistant user interface.

---

## Initial Setup (Pairing the Charger)

### Automatic Discovery
OpenEVSE chargers announce themselves on your local network using Zeroconf / mDNS.
1. When detected, a notification or card will appear under **Settings** ➔ **Devices & Services**.
2. Click **Configure** on the discovered OpenEVSE card.
3. Review or confirm the host details and enter authentication credentials if required.

### Manual Setup
If your charger is not discovered automatically (e.g., across separate VLANs or subnets):
1. Navigate to **Settings** ➔ **Devices & Services**.
2. Click the **+ Add Integration** button in the lower-right corner.
3. Search for **OpenEVSE** and select it.
4. Enter the connection settings:
   - **Host / IP**: The hostname or local IP address of your OpenEVSE charger (e.g. `openevse.local` or `192.168.1.50`).
   - **Port**: Default is `80` (or `443` if SSL/TLS is enabled).
   - **Username** & **Password**: Optional HTTP Basic Auth credentials if set in your OpenEVSE WiFi firmware.

::: tip HTTPS / SSL
If configuring the integration with HTTPS, ensure your certificates are properly loaded on the OpenEVSE device first.
:::

---

## Options & Advanced Configuration

You can customize how the OpenEVSE integration behaves and link external Home Assistant sensors for solar diversion, grid management, and EV battery status:

1. Go to **Settings** ➔ **Devices & Services** ➔ **OpenEVSE**.
2. Click the **Configure** button on the integration entry.

| Option | Description |
| :--- | :--- |
| **Grid Sensor** | Sensor measuring net electrical grid import/export in Watts (`W`). |
| **Invert Grid** | Toggle this if your grid sensor uses negative numbers for power export. |
| **Solar Sensor** | Sensor measuring total active rooftop solar PV generation in Watts (`W`). |
| **Voltage Sensor** | Sensor providing real-time grid AC voltage in Volts (`V`). |
| **Shaper Sensor** | Sensor measuring total active household consumption (excluding the EVSE) in Watts (`W`) to dynamically scale back charging and protect main panels from tripping. |
| **Vehicle State of Charge Sensor** | Vehicle battery percentage entity (`%`), typically from your vehicle's connected car integration. |
| **Vehicle Range Sensor** | Vehicle remaining range sensor (`km` or `mi`). |
| **Vehicle Time-to-Full Sensor** | Estimated duration until full battery charge. |
| **Home Battery SOC Sensor** | Stationary home storage battery state of charge (`%`). |
| **Home Battery Power Sensor** | Stationary home storage battery current charge/discharge power (`W`). |
| **GitHub Personal Access Token** | Optional GitHub Personal Access Token to avoid rate limits when fetching latest firmware updates. |
