from homeassistant.const import (
    ELECTRIC_CURRENT_AMPERE,
    ENERGY_KILO_WATT_HOUR,
    TEMP_CELSIUS,
    TIME_MINUTES,
    ELECTRIC_POTENTIAL_VOLT,
)

CONF_NAME = "name"
DEFAULT_HOST = "openevse.local"
DEFAULT_NAME = "OpenEVSE"
DOMAIN = "openevse"
COORDINATOR = "coordinator"
VERSION = "1.0.0"
ISSUE_URL = "http://github.com/firstof9/openevse/"
PLATFORMS = ["sensor", "switch"]
USER_AGENT = "Home Assistant"

# Name, unit of measure, property, icon
SENSOR_TYPES = {
    "status": ["Charging Status", None, "status", "mdi:ev-station"],
    "charge_time": [
        "Charge Time Elapsed",
        TIME_MINUTES,
        "charge_time_elapsed",
        "mdi:camera-timer",
    ],
    "ambient_temp": ["Ambient Temperature", TEMP_CELSIUS, "ambient_temperature", None],
    "ir_temp": ["IR Temperature", TEMP_CELSIUS, "ir_temperature", None],
    "rtc_temp": ["RTC Temperature", TEMP_CELSIUS, "rtc_temperature", None],
    "usage_session": [
        "Usage this Session",
        ENERGY_KILO_WATT_HOUR,
        "usage_session",
        "mdi:gauge",
    ],
    "usage_total": ["Total Usage", ENERGY_KILO_WATT_HOUR, "usage_total", "mdi:gauge"],
    "firmware_version": [
        "Controller Firmware",
        None,
        "firmware_version",
        "mdi:package-up",
    ],
    "protocol_version": [
        "Protocol Version",
        None,
        "protocol_version",
        "mdi:package-up",
    ],
    "ambient_threshold": ["Ambient Threshold", TEMP_CELSIUS, "ambient_threshold", None],
    "charging_voltage": [
        "Charging Voltage",
        ELECTRIC_POTENTIAL_VOLT,
        "charging_voltage",
        "mdi:sine-wave",
    ],
    "charge_limit": [
        "Charge Limit",
        ENERGY_KILO_WATT_HOUR,
        "charge_limit",
        "mdi:gauge",
    ],
    "charging_current": [
        "Charging Current",
        ELECTRIC_CURRENT_AMPERE,
        "charging_current",
        "mdi:sine-wave",
    ],
    "service_level": ["Service Level", None, "service_level", "mdi:leaf"],
    "max_amps": ["Max Amps", ELECTRIC_CURRENT_AMPERE, "max_amps", "mdi:sine-wave"],
    "current_capacity": [
        "Current Capacity",
        ELECTRIC_CURRENT_AMPERE,
        "current_capacity",
        "mdi:sine-wave",
    ],
    "time_limit": ["Time Limit", TIME_MINUTES, "time_limit", "mdi:camera-timer"],
    "wifi_version": ["Wifi Fimrware Version", None, "wifi_version", "mdi:package-up"],
}

SWITCH_TYPES = ["Sleep Mode"]
