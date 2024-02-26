"""Constants for OpenEVSE."""

from __future__ import annotations

from typing import Final

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.components.button import ButtonDeviceClass, ButtonEntityDescription
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfLength,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.helpers.entity import EntityCategory

from .entity import OpenEVSESelectEntityDescription, OpenEVSESwitchEntityDescription

# config flow
CONF_NAME = "name"
CONF_SERIAL = "id"
CONF_TYPE = "type"
CONF_GRID = "grid"
CONF_SOLAR = "solar"
CONF_INVERT = "invert_grid"
CONF_VOLTAGE = "voltage"
DEFAULT_HOST = "openevse.local"
DEFAULT_NAME = "OpenEVSE"

# hass.data attribues
UNSUB_LISTENERS = "unsub_listeners"

DOMAIN = "openevse"
COORDINATOR = "coordinator"
FW_COORDINATOR = "fw_coordinator"
VERSION = "1.0.0"
ISSUE_URL = "http://github.com/firstof9/openevse/"
PLATFORMS = ["binary_sensor", "button", "sensor", "select", "switch", "update"]
USER_AGENT = "Home Assistant"
MANAGER = "manager"

SERVICE_SET_OVERRIDE = "set_override"
SERVICE_CLEAR_OVERRIDE = "clear_override"
SERVICE_SET_LIMIT = "set_limit"
SERVICE_CLEAR_LIMIT = "clear_limit"
SERVICE_GET_LIMIT = "get_limit"
SERVICE_MAKE_CLAIM = "make_claim"
SERVICE_LIST_CLAIMS = "list_claims"
SERVICE_RELEASE_CLAIM = "release_claim"

# attributes
ATTR_DEVICE_ID = "device_id"
ATTR_STATE = "state"
ATTR_CHARGE_CURRENT = "charge_current"
ATTR_MAX_CURRENT = "max_current"
ATTR_ENERGY_LIMIT = "energy_limit"
ATTR_TIME_LIMIT = "time_limit"
ATTR_AUTO_RELEASE = "auto_release"
ATTR_TYPE = "type"
ATTR_VALUE = "value"

SERVICE_LEVELS = ["1", "2", "A"]
DIVERT_MODE = ["fast", "eco"]

# Name, unit of measure, property, icon, device class, state class
SENSOR_TYPES: Final[dict[str, SensorEntityDescription]] = {
    "status": SensorEntityDescription(
        key="status", name="Station Status", icon="mdi:ev-station"
    ),
    "state": SensorEntityDescription(key="state", name="Charging Status"),
    "charge_time_elapsed": SensorEntityDescription(
        key="charge_time_elapsed",
        name="Charge Time Elapsed",
        icon="mdi:camera-timer",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
    ),
    "ambient_temperature": SensorEntityDescription(
        key="ambient_temperature",
        name="Ambient Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    "ir_temperature": SensorEntityDescription(
        key="ir_temperature",
        name="IR Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=False,
    ),
    "rtc_temperature": SensorEntityDescription(
        key="rtc_temperature",
        name="RTC Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=False,
    ),
    "esp_temperature": SensorEntityDescription(
        key="esp_temperature",
        name="ESP32 Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=False,
    ),
    "usage_session": SensorEntityDescription(
        key="usage_session",
        name="Usage this Session",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        suggested_display_precision=1,
    ),
    "usage_total": SensorEntityDescription(
        key="usage_total",
        name="Total Usage",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        suggested_display_precision=1,
    ),
    "openevse_firmware": SensorEntityDescription(
        key="openevse_firmware",
        name="Controller Firmware",
        icon="mdi:package-up",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "protocol_version": SensorEntityDescription(
        key="protocol_version",
        name="Protocol Version",
        icon="mdi:package-up",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    "charging_voltage": SensorEntityDescription(
        key="charging_voltage",
        name="Charging Voltage",
        icon="mdi:sine-wave",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        suggested_display_precision=1,
    ),
    "charging_current": SensorEntityDescription(
        key="charging_current",
        name="Charging Current",
        icon="mdi:sine-wave",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        suggested_display_precision=1,
    ),
    "service_level": SensorEntityDescription(
        key="service_level",
        name="Service Level",
        icon="mdi:leaf",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "max_amps": SensorEntityDescription(
        key="max_amps",
        name="Max Amps",
        icon="mdi:sine-wave",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "min_amps": SensorEntityDescription(
        key="min_amps",
        name="Min Amps",
        icon="mdi:sine-wave",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "current_capacity": SensorEntityDescription(
        key="current_capacity",
        name="Current Capacity",
        icon="mdi:sine-wave",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "wifi_firmware": SensorEntityDescription(
        key="wifi_firmware",
        name="WiFi Firmware Version",
        icon="mdi:package-up",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "charging_power": SensorEntityDescription(
        key="charging_power",
        name="Current Power Usage",
        icon="mdi:flash",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    "wifi_signal": SensorEntityDescription(
        key="wifi_signal",
        name="WiFi Signal Strength",
        icon="mdi:wifi",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "ammeter_scale_factor": SensorEntityDescription(
        key="ammeter_scale_factor",
        name="Sensor Scale",
        icon="mdi:scale",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    "charge_mode": SensorEntityDescription(
        name="Divert Mode",
        key="charge_mode",
        icon="mdi:solar-power",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "available_current": SensorEntityDescription(
        name="PV Available Current",
        key="available_current",
        icon="mdi:sine-wave",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        suggested_display_precision=1,
    ),
    "smoothed_available_current": SensorEntityDescription(
        name="PV Smoothed Available Current",
        key="smoothed_available_current",
        icon="mdi:sine-wave",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        suggested_display_precision=1,
    ),
    "charge_rate": SensorEntityDescription(
        name="PV Charge Rate",
        key="charge_rate",
        icon="mdi:sine-wave",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
    ),
    "shaper_live_power": SensorEntityDescription(
        name="Shaper Power",
        key="shaper_live_power",
        icon="mdi:flash",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        entity_registry_enabled_default=False,
    ),
    "shaper_current": SensorEntityDescription(
        name="Shaper Current",
        key="shaper_current_power",
        icon="mdi:flash",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    "shaper_max_power": SensorEntityDescription(
        name="Shaper Max Power",
        key="shaper_max_power",
        icon="mdi:flash",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        entity_registry_enabled_default=False,
    ),
    "vehicle_soc": SensorEntityDescription(
        name="Vehicle Battery Level",
        key="vehicle_soc",
        icon="mdi:battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    "vehicle_range": SensorEntityDescription(
        name="Vehicle Range",
        key="vehicle_range",
        icon="mdi:ev-station",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        entity_registry_enabled_default=False,
    ),
    "vehicle_eta": SensorEntityDescription(
        name="Vehicle Charge Completion",
        key="vehicle_eta",
        icon="mdi:car-electric",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    "total_day": SensorEntityDescription(
        key="total_day",
        name="Usage (Today)",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        entity_registry_enabled_default=False,
    ),
    "total_week": SensorEntityDescription(
        key="total_week",
        name="Usage (Week)",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        entity_registry_enabled_default=False,
    ),
    "total_month": SensorEntityDescription(
        key="total_month",
        name="Usage (Month)",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        entity_registry_enabled_default=False,
    ),
    "total_year": SensorEntityDescription(
        key="total_year",
        name="Usage (Year)",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        entity_registry_enabled_default=False,
    ),
}

SWITCH_TYPES: Final[dict[str, OpenEVSESwitchEntityDescription]] = {
    "sleep_mode": OpenEVSESwitchEntityDescription(
        name="Sleep Mode",
        key="state",
        toggle_command="toggle_override",
        device_class=SwitchDeviceClass.SWITCH,
        entity_registry_enabled_default=False,
    ),
    "sleep_mode_new": OpenEVSESwitchEntityDescription(
        name="Sleep Mode (new)",
        key="state",
        toggle_command="claim",
        device_class=SwitchDeviceClass.SWITCH,
        entity_registry_enabled_default=False,
    ),
    "manual_override": OpenEVSESwitchEntityDescription(
        name="Manual Override",
        key="manual_override",
        toggle_command="toggle_override",
        device_class=SwitchDeviceClass.SWITCH,
    ),
    "divertmode": OpenEVSESwitchEntityDescription(
        name="Solar PV Divert",
        key="divert_active",
        toggle_command="divert_mode",
        device_class=SwitchDeviceClass.SWITCH,
    ),
}

# Name, options, command, entity category
SELECT_TYPES: Final[dict[str, OpenEVSESelectEntityDescription]] = {
    # "service_level": OpenEVSESelectEntityDescription(
    #     name="Service Level",
    #     key="service_level",
    #     default_options=SERVICE_LEVELS,
    #     command="$SL",
    #     entity_category=EntityCategory.CONFIG,
    # ),
    "max_current_soft": OpenEVSESelectEntityDescription(
        name="Max Current",
        key="current_capacity",
        default_options=None,
        command="set_current",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    "charge_mode": OpenEVSESelectEntityDescription(
        name="Divert Mode",
        key="charge_mode",
        default_options=DIVERT_MODE,
        command="set_charge_mode",
        entity_category=EntityCategory.CONFIG,
    ),
}

# key: name
BINARY_SENSORS: Final[dict[str, BinarySensorEntityDescription]] = {
    "ota_update": BinarySensorEntityDescription(
        name="OTA Update",
        key="ota_update",
        device_class=BinarySensorDeviceClass.UPDATE,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
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
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    "shaper_active": BinarySensorEntityDescription(
        name="Shaper Active",
        key="shaper_active",
        device_class=BinarySensorDeviceClass.POWER,
    ),
    "has_limit": BinarySensorEntityDescription(
        name="Limit Active",
        key="has_limit",
        device_class=BinarySensorDeviceClass.POWER,
        entity_registry_enabled_default=False,
    ),
    "mqtt_connected": BinarySensorEntityDescription(
        name="MQTT Connected",
        key="mqtt_connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
}

BUTTON_TYPES: Final[dict[str, ButtonEntityDescription]] = {
    "restart_wifi": ButtonEntityDescription(
        key="restart_wifi",
        name="Restart WiFi",
        device_class=ButtonDeviceClass.RESTART,
        entity_category=EntityCategory.CONFIG,
    ),
    "restart_evse": ButtonEntityDescription(
        key="restart_evse",
        name="Restart EVSE",
        device_class=ButtonDeviceClass.RESTART,
        entity_category=EntityCategory.CONFIG,
    ),
}
