# Installation

There are two primary ways to install the OpenEVSE integration: using the **Home Assistant Community Store (HACS)** or performing a **Manual Installation**.

---

## 1. Installation via HACS (Recommended)

Installing via HACS provides automatic update notifications and straightforward one-click updates.

### Quick Link
Click the button below to jump straight to the repository in your Home Assistant instance:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=firstof9&repository=openevse&category=integration)

### Step-by-Step in HACS
1. Open **HACS** from your Home Assistant sidebar.
2. In the top right corner, click the **three dots** menu and select **Custom repositories**.
3. In the dialog:
   - **Repository URL**: `https://github.com/firstof9/openevse`
   - **Category**: `Integration`
4. Click **Add**.
5. Search for **OpenEVSE** in the integrations list and click **Download** / **Install**.
6. **Restart Home Assistant** to load the custom component files.

---

## 2. Manual Installation

::: warning
Manual installation requires you to manually copy new releases when upgrading. HACS is strongly recommended.
:::

1. Access your Home Assistant configuration directory (where `configuration.yaml` is located).
2. Locate or create the directory named `custom_components`.
3. Inside `custom_components`, create a folder named `openevse`.
4. Download the latest release from the [GitHub Releases page](https://github.com/firstof9/openevse/releases).
5. Extract the files from `custom_components/openevse/` into your Home Assistant's `config/custom_components/openevse/` folder.
   Your directory structure should look like:
   ```text
   config/
   └── custom_components/
       └── openevse/
           ├── __init__.py
           ├── manifest.json
           ├── sensor.py
           ├── switch.py
           └── ...
   ```
6. **Restart Home Assistant**.

---

## Next Steps

Once installed, proceed to the [Configuration Guide](./configuration.md) to pair your OpenEVSE charger.
