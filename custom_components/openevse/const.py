from __future__ import annotations

from typing import Final

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.const import (
    ELECTRIC_CURRENT_AMPERE,
    ELECTRIC_POTENTIAL_VOLT,
    ENERGY_KILO_WATT_HOUR,
    ENTITY_CATEGORY_CONFIG,
    ENTITY_CATEGORY_DIAGNOSTIC,
    POWER_WATT,
    SIGNAL_STRENGTH_DECIBELS,
    TEMP_CELSIUS,
    TIME_MINUTES,
)

from .entity import OpenEVSESelectEntityDescription, OpenEVSESwitchEntityDescription

CONF_NAME = "name"
DEFAULT_HOST = "openevse.local"
DEFAULT_NAME = "OpenEVSE"
DOMAIN = "openevse"
COORDINATOR = "coordinator"
VERSION = "1.0.0"
ISSUE_URL = "http://github.com/firstof9/openevse/"
PLATFORMS = ["binary_sensor", "sensor", "select", "switch"]
USER_AGENT = "Home Assistant"
MANAGER = "manager"

SERVICE_LEVELS = ["1", "2", "A"]
DIVERT_MODE = ["normal", "eco"]

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
        "openevse_firmware",
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
    "charging_voltage": [
        "Charging Voltage",
        ELECTRIC_POTENTIAL_VOLT,
        "charging_voltage",
        "mdi:sine-wave",
        DEVICE_CLASS_VOLTAGE,
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
        None,
    ],
    "min_amps": [
        "Min Amps",
        ELECTRIC_CURRENT_AMPERE,
        "min_amps",
        "mdi:sine-wave",
        DEVICE_CLASS_CURRENT,
        None,
    ],
    "current_capacity": [
        "Current Capacity",
        ELECTRIC_CURRENT_AMPERE,
        "current_capacity",
        "mdi:sine-wave",
        DEVICE_CLASS_CURRENT,
        None,
    ],
    "wifi_firmware": [
        "Wifi Fimrware Version",
        None,
        "wifi_firmware",
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

# Name, options, command, entity category
SELECT_TYPES: Final[dict[str, OpenEVSESelectEntityDescription]] = {
    "service_level": OpenEVSESelectEntityDescription(
        name="Service Level",
        key="service_level",
        default_options=SERVICE_LEVELS,
        command="$SL",
        entity_category=ENTITY_CATEGORY_CONFIG,
    ),
    "current_capacity": OpenEVSESelectEntityDescription(
        name="Max Current",
        key="current_capacity",
        default_options=None,
        command="$SC",
        entity_category=ENTITY_CATEGORY_CONFIG,
    ),
    "divertmode": OpenEVSESelectEntityDescription(
        name="Divert Mode",
        key="divertmode",
        default_options=DIVERT_MODE,
        command="divert_mode",
        entity_category=ENTITY_CATEGORY_CONFIG,
    ),
}

# key: name
BINARY_SENSORS: Final[dict[str, BinarySensorEntityDescription]] = {
    "ota_update": BinarySensorEntityDescription(
        name="OTA Update",
        key="ota_update",
        device_class=BinarySensorDeviceClass.UPDATE,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    "vehicle": BinarySensorEntityDescription(
        name="Vehicle Connected",
        key="vehicle",
        device_class=BinarySensorDeviceClass.PLUG,
    ),
    "manual_override": BinarySensorEntityDescription(
        name="Manual Override",
        key="manual_override",
        device_class=BinarySensorDeviceClass.POWER,
    ),
    "divert_active": BinarySensorEntityDescription(
        name="Divert Active",
        key="divert_active",
        device_class=BinarySensorDeviceClass.POWER,
    ),
    "using_ethernet": BinarySensorEntityDescription(
        name="Ethernet Connected",
        key="using_ethernet",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
}
