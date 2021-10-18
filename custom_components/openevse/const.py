from __future__ import annotations

from typing import Final

from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL,
    STATE_CLASS_TOTAL_INCREASING,
    SensorEntityDescription,
)

from homeassistant.const import (
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_TIMESTAMP,
    DEVICE_CLASS_VOLTAGE,
    ELECTRIC_CURRENT_AMPERE,
    ELECTRIC_POTENTIAL_VOLT,
    ENTITY_CATEGORY_DIAGNOSTIC,
    ENERGY_KILO_WATT_HOUR,
    POWER_WATT,
    SIGNAL_STRENGTH_DECIBELS,
    TEMP_CELSIUS,
    TIME_MINUTES,
)

CONF_NAME = "name"
DEFAULT_HOST = "openevse.local"
DEFAULT_NAME = "OpenEVSE"
DOMAIN = "openevse"
COORDINATOR = "coordinator"
VERSION = "1.0.0"
ISSUE_URL = "http://github.com/firstof9/openevse/"
PLATFORMS = ["sensor", "select", "switch"]
USER_AGENT = "Home Assistant"

SERVICE_LEVELS = ["1", "2", "A"]

# Name, unit of measure, property, icon, device class, state class
SENSOR_TYPES: Final[dict[str, SensorEntityDescription]] = {
    "status": SensorEntityDescription(
        key="status", name="Charging Status", icon="mdi:ev-station"
    ),
    "charge_time_elapsed": SensorEntityDescription(
        key="charge_time_elapsed",
        name="Charge Time Elapsed",
        icon="mdi:camera-timer",
        device_class=DEVICE_CLASS_TIMESTAMP,
    ),
    "ambient_temperature": SensorEntityDescription(
        key="ambient_temperature",
        name="Ambient Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=DEVICE_CLASS_TEMPERATURE,
    ),
    "ir_temperature": SensorEntityDescription(
        key="ir_temperature",
        name="IR Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=DEVICE_CLASS_TEMPERATURE,
    ),
    "rtc_temperature": SensorEntityDescription(
        key="rtc_temperature",
        name="RTC Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=DEVICE_CLASS_TEMPERATURE,
    ),
    "esp_temperature": SensorEntityDescription(
        key="esp_temperature",
        name="ESP32 Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=DEVICE_CLASS_TEMPERATURE,
    ),
    "usage_session": SensorEntityDescription(
        key="usage_session",
        name="Usage this Session",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=STATE_CLASS_TOTAL,
        device_class=DEVICE_CLASS_ENERGY,
    ),
    "usage_total": SensorEntityDescription(
        key="usage_total",
        name="Total Usage",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=STATE_CLASS_TOTAL,
        device_class=STATE_CLASS_TOTAL_INCREASING,
    ),
    "openevse_firmware": SensorEntityDescription(
        key="openevse_firmware",
        name="Controller Firmware",
        icon="mdi:package-up",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    "protocol_version": SensorEntityDescription(
        key="protocol_version",
        name="Protocol Version",
        icon="mdi:package-up",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    "charging_voltage": SensorEntityDescription(
        key="charging_voltage",
        name="Charging Voltage",
        icon="mdi:sine-wave",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=DEVICE_CLASS_VOLTAGE,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    "charging_current": SensorEntityDescription(
        key="charging_current",
        name="Charging Current",
        icon="mdi:sine-wave",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=DEVICE_CLASS_CURRENT,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    "service_level": SensorEntityDescription(
        key="service_level",
        name="Service Level",
        icon="mdi:leaf",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    "max_amps": SensorEntityDescription(
        key="max_amps",
        name="Max Amps",
        icon="mdi:sine-wave",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        device_class=DEVICE_CLASS_CURRENT,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    "min_amps": SensorEntityDescription(
        key="min_amps",
        name="Min Amps",
        icon="mdi:sine-wave",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        device_class=DEVICE_CLASS_CURRENT,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    "current_capacity": SensorEntityDescription(
        key="current_capacity",
        name="Current Capacity",
        icon="mdi:sine-wave",
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        device_class=DEVICE_CLASS_CURRENT,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    "wifi_firmware": SensorEntityDescription(
        key="wifi_firmware",
        name="Wifi Fimrware Version",
        icon="mdi:package-up",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    "current_power": SensorEntityDescription(
        key="current_power",
        name="Current Power Usage",
        icon="mdi:gauge",
        native_unit_of_measurement=POWER_WATT,
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    "wifi_signal": SensorEntityDescription(
        key="wifi_signal",
        name="Wifi Signal Strength",
        icon="mdi:wifi",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    "ammeter_scale_factor": SensorEntityDescription(
        key="ammeter_scale_factor",
        name="Sensor Scale",
        icon="mdi:scale",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
}

SWITCH_TYPES = ["Sleep Mode"]

# Name, unit of measure, options, command
SELECT_TYPES = {
    "service_level": ["Service Level", None, SERVICE_LEVELS, "$SL"],
    "current_capacity": ["Max Current", ELECTRIC_CURRENT_AMPERE, None, "$SC"],
}
