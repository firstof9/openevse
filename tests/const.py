"""Openevse tests consts."""

FW_DATA = {
    "latest_version": "4.1.7",
    "release_summary": "## What's Changed\r\n* add upload_progress event to websocket by @KipK in https://github.com/OpenEVSE/ESP32_WiFi_V4.x/pull/471\r\n* improvment & fixes of MQTT /override topic by @KipK in https://github.com/OpenEVSE/ESP32_WiFi_V4.x/pull/485\r\n* add \"claims_ve..",
    "release_url": "https://github.com/OpenEVSE/ESP32_WiFi_V4.x/releases/tag/4.1.7",
}

GETFW_DATA = ("4.1.7", "openevse_wifi_v1")

CHARGER_DATA = {
    "status": "disabled",
    "state": "Sleeping",
    "charge_time_elapsed": 17832,
    "ambient_temperature": 29.6,
    "ir_temperature": None,
    "rtc_temperature": 29.6,
    "esp_temperature": 32.25,
    "usage_session": 29509.52,
    "usage_total": 7642350,
    "openevse_firmware": "7.1.3",
    "protocol_version": None,
    "charging_voltage": 240,
    "charging_current": 0,
    "service_level": 2,
    "max_amps": 48,
    "min_amps": 6,
    "current_capacity": 48,
    "wifi_firmware": "4.1.7",
    "charging_power": 0,
    "wifi_signal": -66,
    "ammeter_scale_factor": 220,
    "divertmode": "normal",
    "charge_rate": 0,
    "shaper_live_power": 0,
    "shaper_current": 0,
    "shaper_max_power": None,
    "vehicle_soc": None,
    "vehicle_range": None,
    "vehicle_eta": None,
    "ota_update": False,
    "vehicle": False,
    "manual_override": False,
    "divert_active": False,
    "using_ethernet": False,
    "shaper_active": False,
    "max_current_soft": 48,
}
CONFIG_DATA = {
    "name": "openevse",
    "host": "openevse.test.tld",
    "username": "",
    "password": "",
}
CONFIG_DATA_GRID = {
    "name": "openevse",
    "host": "openevse.test.tld",
    "username": "",
    "password": "",
    "grid": "sensor.grid_usage",
    "invert_grid": False,
}
CONFIG_DATA_SOLAR = {
    "name": "openevse",
    "host": "openevse.test.tld",
    "username": "",
    "password": "",
    "solar": "sensor.solar_production",
    "voltage": "sensor.grid_voltage",
    "invert_grid": False,
}
