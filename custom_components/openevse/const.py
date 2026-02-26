"""Constants for OpenEVSE."""

from __future__ import annotations

from typing import Final

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.components.button import ButtonDeviceClass, ButtonEntityDescription
from homeassistant.components.number import NumberDeviceClass, NumberMode
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS,
    Platform,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfLength,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.helpers.entity import EntityCategory

from .entity import (
    OpenEVSELightEntityDescription,
    OpenEVSENumberEntityDescription,
    OpenEVSESelectEntityDescription,
    OpenEVSESensorEntityDescription,
    OpenEVSESwitchEntityDescription,
)

# config flow
CONF_NAME = "name"
CONF_SERIAL = "id"
CONF_TYPE = "type"
CONF_GRID = "grid"
CONF_SOLAR = "solar"
CONF_INVERT = "invert_grid"
CONF_VOLTAGE = "voltage"
CONF_SHAPER = "shaper"
DEFAULT_HOST = "openevse.local"
DEFAULT_NAME = "OpenEVSE"

# hass.data attributes
UNSUB_LISTENERS = "unsub_listeners"

DOMAIN = "openevse"
COORDINATOR = "coordinator"
FW_COORDINATOR = "fw_coordinator"
VERSION = "1.0.0"
ISSUE_URL = "http://github.com/firstof9/openevse/"
PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.LIGHT,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SELECT,
    Platform.SWITCH,
    Platform.UPDATE,
]
USER_AGENT = "Home Assistant"
MANAGER = "manager"

TIMEOUT_ERROR = (
    "Timeout error connecting to device: %s, please check your network connection."
)

SERVICE_SET_OVERRIDE = "set_override"
SERVICE_CLEAR_OVERRIDE = "clear_override"
SERVICE_SET_LIMIT = "set_limit"
SERVICE_CLEAR_LIMIT = "clear_limit"
SERVICE_GET_LIMIT = "get_limit"
SERVICE_MAKE_CLAIM = "make_claim"
SERVICE_LIST_CLAIMS = "list_claims"
SERVICE_RELEASE_CLAIM = "release_claim"
SERVICE_LIST_OVERRIDES = "list_overrides"

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
OVERRIDE_STATE = ["active", "auto", "disabled"]

# Name, unit of measure, property, icon, device class, state class
SENSOR_TYPES: Final[dict[str, OpenEVSESensorEntityDescription]] = {
    "status": OpenEVSESensorEntityDescription(
        key="status", name="Station Status", icon="mdi:ev-station"
    ),
    "state": OpenEVSESensorEntityDescription(key="state", name="Charging Status"),
    "charge_time_elapsed": OpenEVSESensorEntityDescription(
        key="charge_time_elapsed",
        name="Charge Time Elapsed",
        icon="mdi:camera-timer",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        suggested_unit_of_measurement=UnitOfTime.MINUTES,
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.DURATION,
        suggested_display_precision=1,
    ),
    "ambient_temperature": OpenEVSESensorEntityDescription(
        key="ambient_temperature",
        name="Ambient Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    "ir_temperature": OpenEVSESensorEntityDescription(
        key="ir_temperature",
        name="IR Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=False,
    ),
    "rtc_temperature": OpenEVSESensorEntityDescription(
        key="rtc_temperature",
        name="RTC Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=False,
    ),
    "esp_temperature": OpenEVSESensorEntityDescription(
        key="esp_temperature",
        name="ESP32 Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=False,
    ),
    "usage_session": OpenEVSESensorEntityDescription(
        key="usage_session",
        name="Usage this Session",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        suggested_display_precision=1,
    ),
    "usage_total": OpenEVSESensorEntityDescription(
        key="usage_total",
        name="Total Usage",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        suggested_display_precision=1,
    ),
    "openevse_firmware": OpenEVSESensorEntityDescription(
        key="openevse_firmware",
        name="Controller Firmware",
        icon="mdi:package-up",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "protocol_version": OpenEVSESensorEntityDescription(
        key="protocol_version",
        name="Protocol Version",
        icon="mdi:package-up",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    "charging_voltage": OpenEVSESensorEntityDescription(
        key="charging_voltage",
        name="Charging Voltage",
        icon="mdi:sine-wave",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        suggested_display_precision=1,
    ),
    "charging_current": OpenEVSESensorEntityDescription(
        key="charging_current",
        name="Charging Current",
        icon="mdi:sine-wave",
        native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
        suggested_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        suggested_display_precision=1,
    ),
    "service_level": OpenEVSESensorEntityDescription(
        key="service_level",
        name="Service Level",
        icon="mdi:leaf",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "max_amps": OpenEVSESensorEntityDescription(
        key="max_amps",
        name="Max Amps",
        icon="mdi:sine-wave",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "min_amps": OpenEVSESensorEntityDescription(
        key="min_amps",
        name="Min Amps",
        icon="mdi:sine-wave",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "current_capacity": OpenEVSESensorEntityDescription(
        key="current_capacity",
        name="Current Capacity",
        icon="mdi:sine-wave",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "wifi_firmware": OpenEVSESensorEntityDescription(
        key="wifi_firmware",
        name="WiFi Firmware Version",
        icon="mdi:package-up",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "charging_power": OpenEVSESensorEntityDescription(
        key="charging_power",
        name="Current Power Usage (Calculated)",
        icon="mdi:flash",
        native_unit_of_measurement=UnitOfPower.MILLIWATT,
        suggested_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    "wifi_signal": OpenEVSESensorEntityDescription(
        key="wifi_signal",
        name="WiFi Signal Strength",
        icon="mdi:wifi",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "ammeter_scale_factor": OpenEVSESensorEntityDescription(
        key="ammeter_scale_factor",
        name="Sensor Scale",
        icon="mdi:scale",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    "divertmode": OpenEVSESensorEntityDescription(
        name="Divert Mode",
        key="divertmode",
        icon="mdi:solar-power",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "available_current": OpenEVSESensorEntityDescription(
        name="PV Available Current",
        key="available_current",
        icon="mdi:sine-wave",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        suggested_display_precision=1,
    ),
    "smoothed_available_current": OpenEVSESensorEntityDescription(
        name="PV Smoothed Available Current",
        key="smoothed_available_current",
        icon="mdi:sine-wave",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        suggested_display_precision=1,
    ),
    "charge_rate": OpenEVSESensorEntityDescription(
        name="PV Charge Rate",
        key="charge_rate",
        icon="mdi:sine-wave",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
    ),
    "shaper_live_power": OpenEVSESensorEntityDescription(
        name="Shaper Power",
        key="shaper_live_power",
        icon="mdi:flash",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        entity_registry_enabled_default=False,
        min_version="4.1.0",
    ),
    "shaper_available_current": OpenEVSESensorEntityDescription(
        name="Shaper Current Available",
        key="shaper_available_current",
        icon="mdi:flash",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        min_version="4.1.0",
    ),
    "shaper_max_power": OpenEVSESensorEntityDescription(
        name="Shaper Max Power",
        key="shaper_max_power",
        icon="mdi:flash",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        entity_registry_enabled_default=False,
        min_version="4.1.0",
    ),
    "vehicle_soc": OpenEVSESensorEntityDescription(
        name="Vehicle Battery Level",
        key="vehicle_soc",
        icon="mdi:battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        min_version="4.1.0",
    ),
    "vehicle_range": OpenEVSESensorEntityDescription(
        name="Vehicle Range",
        key="vehicle_range",
        icon="mdi:ev-station",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        entity_registry_enabled_default=False,
        min_version="4.1.0",
    ),
    "vehicle_eta": OpenEVSESensorEntityDescription(
        name="Vehicle Charge Completion",
        key="vehicle_eta",
        icon="mdi:car-electric",
        device_class=SensorDeviceClass.TIMESTAMP,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        min_version="4.1.0",
    ),
    "total_day": OpenEVSESensorEntityDescription(
        key="total_day",
        name="Usage (Today)",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        entity_registry_enabled_default=False,
        min_version="3.0.0",
    ),
    "total_week": OpenEVSESensorEntityDescription(
        key="total_week",
        name="Usage (Week)",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        entity_registry_enabled_default=False,
        min_version="3.0.0",
    ),
    "total_month": OpenEVSESensorEntityDescription(
        key="total_month",
        name="Usage (Month)",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        entity_registry_enabled_default=False,
        min_version="3.0.0",
    ),
    "total_year": OpenEVSESensorEntityDescription(
        key="total_year",
        name="Usage (Year)",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        entity_registry_enabled_default=False,
        min_version="3.0.0",
    ),
    "max_current": OpenEVSESensorEntityDescription(
        key="max_current",
        name="Max Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "override_state": OpenEVSESensorEntityDescription(
        key="override_state",
        name="Override State",
        entity_category=EntityCategory.DIAGNOSTIC,
        is_async_value=True,
        value="async_override_state",
        min_version="4.1.0",
    ),
    "current_power": OpenEVSESensorEntityDescription(
        key="current_power",
        name="Current Power Usage (Actual)",
        icon="mdi:flash",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        min_version="4.2.2",
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
        min_version="4.1.0",
    ),
    "manual_override": OpenEVSESwitchEntityDescription(
        name="Manual Override",
        key="manual_override",
        toggle_command="toggle_override",
        device_class=SwitchDeviceClass.SWITCH,
        min_version="4.1.0",
    ),
    "divertmode": OpenEVSESwitchEntityDescription(
        name="Solar PV Divert",
        key="divert_active",
        toggle_command="divert_mode",
        device_class=SwitchDeviceClass.SWITCH,
        min_version="4.1.0",
    ),
}

# Name, options, command, entity category
SELECT_TYPES: Final[dict[str, OpenEVSESelectEntityDescription]] = {
    "max_current_soft": OpenEVSESelectEntityDescription(
        name="Charge Rate",
        key="max_current_soft",
        default_options=None,
        command="set_current",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
        is_async_value=True,
        value="async_charge_current",
    ),
    "override_state": OpenEVSESelectEntityDescription(
        key="override_state",
        name="Override State",
        entity_category=EntityCategory.CONFIG,
        default_options=OVERRIDE_STATE,
        is_async_value=True,
        value="async_override_state",
        min_version="4.1.0",
    ),
    "divertmode": OpenEVSESelectEntityDescription(
        name="Divert Mode",
        key="divertmode",
        default_options=DIVERT_MODE,
        command="set_divert_mode",
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
    "shaper_updated": BinarySensorEntityDescription(
        name="Shaper Updated",
        key="shaper_updated",
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

NUMBER_TYPES: Final[dict[str, OpenEVSENumberEntityDescription]] = {
    "max_current_soft": OpenEVSENumberEntityDescription(
        name="Charge Rate",
        key="max_current_soft",
        default_options=None,
        command="set_current",
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=NumberDeviceClass.CURRENT,
        mode=NumberMode.AUTO,
        is_async_value=True,
        value="async_charge_current",
    ),
}

LIGHT_TYPES: Final[dict[str, OpenEVSELightEntityDescription]] = {
    "led_brightness": OpenEVSELightEntityDescription(
        key="led_brightness",
        name="LED Brightness",
        entity_category=EntityCategory.CONFIG,
        command="set_led_brightness",
        min_version="4.1.0",
    ),
}
