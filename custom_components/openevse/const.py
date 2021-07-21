from homeassistant.const import (
    ELECTRICAL_CURRENT_AMPERE,
    ENERGY_KILO_WATT_HOUR,
    TEMP_CELSIUS,
    TIME_MINUTES,
    VOLT,
)

CONF_NAME = "name"
DEFAULT_HOST = "openevse.local"
DEFAULT_NAME = "OpenEVSE"
DOMAIN = "openevse"
COORDINATOR = "coordinator"
VERSION = "1.0.0"
ISSUE_URL = "http://github.com/firstof9/openevse/"
PLATFORMS = ["sensor", "switch"]

# Name, unit of measure, property, icon
SENSOR_TYPES = {
    "status": ["Charging Status", None, "status", None],
    "charge_time": ["Charge Time Elapsed", TIME_MINUTES, "charge_time_elapsed", None],
    "ambient_temp": ["Ambient Temperature", TEMP_CELSIUS, "ambient_temperature", None],
    "ir_temp": ["IR Temperature", TEMP_CELSIUS, "ir_temperature", None],
    "rtc_temp": ["RTC Temperature", TEMP_CELSIUS, "rtc_temperature", None],
    "usage_session": [
        "Usage this Session",
        ENERGY_KILO_WATT_HOUR,
        "usage_session",
        None,
    ],
    "usage_total": ["Total Usage", ENERGY_KILO_WATT_HOUR, "usage_total", None],
    "firmware_version": ["Firmware Version", None, "firmware_version", None],
    "protocol_version": ["Protocol Version", None, "protocol_version", None],
    "ambient_threshold": ["Ambient Threshold", TEMP_CELSIUS, "ambient_threshold", None],
    "charging_voltage": ["Charging Voltage", VOLT, "charging_voltage", None],
    "charge_limit": ["Charge Limit", ENERGY_KILO_WATT_HOUR, "charge_limit", None],
    "charging_current": [
        "Charging Current",
        ELECTRICAL_CURRENT_AMPERE,
        "charging_current",
        None,
    ],
    "service_level": ["Service Level", None, "service_level", None],
    "max_amps": ["Max Amps", ELECTRICAL_CURRENT_AMPERE, "max_amps", None],
    "current_capacity": [
        "Current Capacity",
        ELECTRICAL_CURRENT_AMPERE,
        "current_capacity",
        None,
    ],
    "time_limit": ["Time Limit", None, "time_limit", None],
}

SWITCH_TYPES = ["Sleep Mode"]
