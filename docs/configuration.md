# Configuration

The OpenEVSE integration is configured entirely through the Home Assistant user interface. No YAML editing is required for core integration setup.

---

## Initial Setup

### Auto-Discovery (Zeroconf / mDNS)

If your charger is on the same local subnet as Home Assistant, it will be discovered automatically via **Zeroconf / mDNS**:

1. Go to **Settings ➔ Devices & Services**.
2. Find the **OpenEVSE** card in the *Discovered* section.
3. Click **Configure** and follow the prompts.

### Manual Setup

If auto-discovery does not find your charger (for instance across isolated IoT VLANs):

1. Go to **Settings ➔ Devices & Services**.
2. Click **+ Add Integration** in the bottom-right corner.
3. Search for **OpenEVSE** and select it.
4. Fill in connection details:

| Field | Description | Default |
| :--- | :--- | :--- |
| **Host / IP Address** | Hostname or IP of your charger | `openevse.local` |
| **Username** | HTTP Basic Auth username (if enabled on charger) | *(optional)* |
| **Password** | HTTP Basic Auth password (if enabled on charger) | *(optional)* |

::: tip HTTPS / SSL
If using **HTTPS / SSL**, certificates must be installed on the OpenEVSE device before enabling SSL in the connection step. You can also upload certificates directly through integration options once paired.
:::

---

## Advanced Options Flow

To customize smart charging behaviors, upload certificates, or map power sensors:

1. Navigate to **Settings ➔ Devices & Services ➔ OpenEVSE**.
2. Click **Configure** on the integration card.

The configuration menu presents three paths:
- **Configure sensor entities**: Feed external smart meter and vehicle telemetry into the charger.
- **Install TLS/SSL certificate**: Upload and manage SSL certificates (firmware **4.0.0+**).
- **Install Root CA certificate**: Upload trusted root Certificate Authorities (firmware **4.0.0+**).

---

### External Sensor Inputs

These sensor entities feed external measurements *into* the OpenEVSE charger for real-time solar diversion and circuit overload protection:

| Option | Unit | Description & Purpose |
| :--- | :--- | :--- |
| **Grid Sensor** | `W` (Watts) | Net grid import/export. Positive values represent grid import, negative values represent export to the grid. |
| **Invert Grid** | Toggle | Enable if your power meter reports export as positive numbers. |
| **Solar Sensor** | `W` (Watts) | Total solar PV generation power. |
| **Voltage Sensor** | `V` (Volts) | AC grid line voltage for precise power and amperage calculation. |
| **Shaper Sensor** | `W` (Watts) | Live total household power draw used by Current Shaper to throttle EV charging during heavy home load spikes. |

### Vehicle & Stationary Battery Sensors

Pushes live battery telemetry to the EVSE to support automatic charge termination by percentage, range, or completion time:

| Option | Unit | Description |
| :--- | :--- | :--- |
| **Vehicle State of Charge** | `%` | Vehicle battery percentage from your vehicle integration. |
| **Vehicle Range** | `km` / `mi` | Remaining vehicle driving range. |
| **Vehicle Time-to-Full-Charge** | Timestamp | Estimated charge completion timestamp (ISO-8601 format). |
| **Home Battery SoC** | `%` | Stationary home storage battery percentage. |
| **Home Battery Power** | `W` (Watts) | Home storage battery discharge/charge rate. |

### Additional Settings

| Setting | Purpose |
| :--- | :--- |
| **GitHub Personal Access Token** | Increases GitHub API rate limit from 60 to 5,000 requests/hour for firmware update checks. Generate one at *GitHub ➔ Settings ➔ Developer settings ➔ Personal access tokens* with no extra scopes needed. |

---

## Certificate Management *(Firmware 4.0.0+)*

### Install TLS/SSL Certificate
Upload and install a TLS/SSL server certificate directly onto the OpenEVSE gateway from Home Assistant:

| Field | Description |
| :--- | :--- |
| **Certificate Name** | Identifier/name for the certificate (e.g. `web_server`) |
| **Certificate** | PEM-formatted certificate file content (including `-----BEGIN CERTIFICATE-----` and `-----END CERTIFICATE-----`) |
| **Private Key** | PEM-formatted private key content (including `-----BEGIN PRIVATE KEY-----`) |

### Install Root CA Certificate
Install a trusted Root Certificate Authority onto the gateway (ideal for self-signed or private home PKI certificates):

| Field | Description |
| :--- | :--- |
| **Certificate Name** | Identifier name for the Root CA (e.g. `home_root_ca`) |
| **Certificate** | PEM-formatted Root CA certificate text |

---

## Reconfiguration

To update the host IP address, port, or authentication credentials at any time:

1. Go to **Settings ➔ Devices & Services ➔ OpenEVSE**.
2. Click the **three dots** (`⋮`) menu and select **Reconfigure**.
