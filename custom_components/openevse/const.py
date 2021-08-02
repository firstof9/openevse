from homeassistant.const import (
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_VOLTAGE,
    ELECTRIC_CURRENT_AMPERE,
    ENERGY_KILO_WATT_HOUR,
    TEMP_CELSIUS,
    TIME_MINUTES,
    ELECTRIC_POTENTIAL_VOLT,
    POWER_WATT,
)
from homeassistant.components.sensor import STATE_CLASS_MEASUREMENT

CONF_NAME = "name"
DEFAULT_HOST = "openevse.local"
DEFAULT_NAME = "OpenEVSE"
DOMAIN = "openevse"
COORDINATOR = "coordinator"
VERSION = "1.0.0"
ISSUE_URL = "http://github.com/firstof9/openevse/"
PLATFORMS = ["sensor", "switch"]
USER_AGENT = "Home Assistant"

# Name, unit of measure, property, icon, device class, state class
SENSOR_TYPES = {
    "status": ["Charging Status", None, "status", "mdi:ev-station", None, None],
    "charge_time": [
        "Charge Time Elapsed",
        TIME_MINUTES,
        "charge_time_elapsed",
        "mdi:camera-timer",
        None,
        None,
    ],
    "ambient_temp": [
        "Ambient Temperature",
        TEMP_CELSIUS,
        "ambient_temperature",
        None,
        DEVICE_CLASS_TEMPERATURE,
        STATE_CLASS_MEASUREMENT,
    ],
    "ir_temp": [
        "IR Temperature",
        TEMP_CELSIUS,
        "ir_temperature",
        None,
        DEVICE_CLASS_TEMPERATURE,
        STATE_CLASS_MEASUREMENT,
    ],
    "rtc_temp": [
        "RTC Temperature",
        TEMP_CELSIUS,
        "rtc_temperature",
        None,
        DEVICE_CLASS_TEMPERATURE,
        STATE_CLASS_MEASUREMENT,
    ],
    "usage_session": [
        "Usage this Session",
        ENERGY_KILO_WATT_HOUR,
        "usage_session",
        "mdi:gauge",
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_MEASUREMENT,
    ],
    "usage_total": [
        "Total Usage",
        ENERGY_KILO_WATT_HOUR,
        "usage_total",
        "mdi:gauge",
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_MEASUREMENT,
    ],
    "firmware_version": [
        "Controller Firmware",
        None,
        "firmware_version",
        "mdi:package-up",
        None,
        None,
    ],
    "protocol_version": [
        "Protocol Version",
        None,
        "protocol_version",
        "mdi:package-up",
        None,
        None,
    ],
    "ambient_threshold": [
        "Ambient Threshold",
        TEMP_CELSIUS,
        "ambient_threshold",
        None,
        DEVICE_CLASS_TEMPERATURE,
        None,
    ],
    "charging_voltage": [
        "Charging Voltage",
        ELECTRIC_POTENTIAL_VOLT,
        "charging_voltage",
        "mdi:sine-wave",
        DEVICE_CLASS_VOLTAGE,
        STATE_CLASS_MEASUREMENT,
    ],
    "charge_limit": [
        "Charge Limit",
        ENERGY_KILO_WATT_HOUR,
        "charge_limit",
        "mdi:gauge",
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_MEASUREMENT,
    ],
    "charging_current": [
        "Charging Current",
        ELECTRIC_CURRENT_AMPERE,
        "charging_current",
        "mdi:sine-wave",
        DEVICE_CLASS_CURRENT,
        STATE_CLASS_MEASUREMENT,
    ],
    "service_level": ["Service Level", None, "service_level", "mdi:leaf", None, None],
    "max_amps": [
        "Max Amps",
        ELECTRIC_CURRENT_AMPERE,
        "max_amps",
        "mdi:sine-wave",
        DEVICE_CLASS_CURRENT,
        STATE_CLASS_MEASUREMENT,
    ],
    "current_capacity": [
        "Current Capacity",
        ELECTRIC_CURRENT_AMPERE,
        "current_capacity",
        "mdi:sine-wave",
        DEVICE_CLASS_CURRENT,
        STATE_CLASS_MEASUREMENT,
    ],
    "time_limit": [
        "Time Limit",
        TIME_MINUTES,
        "time_limit",
        "mdi:camera-timer",
        None,
        None,
    ],
    "wifi_version": [
        "Wifi Fimrware Version",
        None,
        "wifi_version",
        "mdi:package-up",
        None,
        None,
    ],
    "current_power": [
        "Current Power Usage",
        POWER_WATT,
        "current_power",
        "mdi:gauge",
        DEVICE_CLASS_POWER,
        STATE_CLASS_MEASUREMENT,
    ],
}

SWITCH_TYPES = ["Sleep Mode"]
