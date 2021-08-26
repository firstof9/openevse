"""Support for monitoring an OpenEVSE Charger."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import DEVICE_CLASS_ENERGY
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_NAME,
    COORDINATOR,
    DOMAIN,
    SENSOR_TYPES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the OpenEVSE sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    unique_id = entry.entry_id

    sensors = []
    for sensor in SENSOR_TYPES:
        sensors.append(
            OpenEVSESensor(SENSOR_TYPES[sensor], unique_id, coordinator, entry)
        )

    async_add_entities(sensors, False)


class OpenEVSESensor(CoordinatorEntity, SensorEntity):
    """Implementation of an OpenEVSE sensor."""

    def __init__(
        self, sensor_type: str, unique_id: str, coordinator: str, config: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config = config
        self._name = SENSOR_TYPES[sensor_type][0]
        self._type = sensor_type
        self._state = None
        self._icon = SENSOR_TYPES[sensor_type][3]
        self._attr_device_class = SENSOR_TYPES[sensor_type][4]
        self._attr_state_class = SENSOR_TYPES[self._type][5]
        self._unique_id = unique_id
        self._data = coordinator.data
        self.coordinator = coordinator
        self._state = None
        self._icon = sensor_description.icon

        self._attr_name = f"{self._config.data[CONF_NAME]}_{self._name}"
        self._attr_unique_id = f"{self._name}_{self._unique_id}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._config.data[CONF_NAME]}_{self._name}"

    @property
    def device_info(self) -> dict:
        """Return a port description for device registry."""
        info = {
            "manufacturer": "OpenEVSE",
            "name": self._config.data[CONF_NAME],
            "connections": {(DOMAIN, self._unique_id)},
        }

        return info

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        data = self.coordinator.data
        if data is None:
            self._state = None
        if self._type in data.keys():
            if self._type == "charge_time":
                self._state = round(data[self._type] / 60, 2)
            elif self._type == "usage_session":
                self._state = round(data[self._type] / 1000, 2)
            elif self._type == "usage_total":
                self._state = round(data[self._type] / 1000, 2)
            elif self._type == "charging_current":
                self._state = round(data[self._type] / 1000, 2)
            elif self._type == "current_power":
                self._state = self.calc_watts()
            else:
                self._state = data[self._type]

        _LOGGER.debug("Sensor [%s] updated value: %s", self._type, self._state)
        self.update_icon()
        return self._state

    @property
    def native_unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        return SENSOR_TYPES[self._type][1]

    @property
    def last_reset(self) -> datetime | None:
        """Return the time when the sensor was last reset, if any."""
        return self._last_reset

    @property
    def icon(self) -> str:
        """Return the icon."""
        return self._icon

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    def update_icon(self) -> None:
        """Update status icon based on state."""
        if self._type == "state":
            if self._state == "unknown":
                self._icon = "mdi:help"
            elif self._state == "not connected":
                self._icon = "mdi:power-plug-off"
            elif self._state == "connected":
                self._icon = "mdi:power-plug"
            elif self._state == "charging":
                self._icon = "mdi:battery-charging"
            elif self._state == "sleeping":
                self._icon = "mdi:sleep"
            elif self._state == "disabled":
                self._icon = "mdi:car-off"
            else:
                self._icon = "mdi:alert-octagon"

    def calc_watts(self) -> float:
        """Calculate Watts based on V*I"""
        return self._data["charging_voltage"] * self._data["charging_current"]

    def update_last_reset(self) -> None:
        """Update last reset attribute"""
        if self._type == "usage_session" and self._state == 0.0:
            self._last_reset = utcnow()
        elif self._type == "usage_session":
            self._last_reset = self._last_reset
        elif self._attr_device_class == DEVICE_CLASS_ENERGY:
            self._last_reset = utc_from_timestamp(0)
        else:
            self._last_reset = None
