"""Support for monitoring an OpenEVSE Charger."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_NAME, COORDINATOR, DOMAIN, MANAGER, SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)

STATUS_ICONS = {
    "unknown": "mdi:help",
    "not connected": "mdi:power-plug-off",
    "connected": "mdi:power-plug",
    "charging": "mdi:battery-charging",
    "sleeping": "mdi:sleep",
    "disabled": "mdi:car-off",
}


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the OpenEVSE sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    unique_id = entry.entry_id

    sensors = []
    for sensor in SENSOR_TYPES:  # pylint: disable=consider-using-dict-items
        sensors.append(
            OpenEVSESensor(SENSOR_TYPES[sensor], unique_id, coordinator, entry)
        )

    async_add_entities(sensors, False)


class OpenEVSESensor(CoordinatorEntity, SensorEntity):
    """Implementation of an OpenEVSE sensor."""

    def __init__(
        self,
        sensor_description: SensorEntityDescription,
        unique_id: str,
        coordinator: str,
        config: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config = config
        self.entity_description = sensor_description
        self._name = sensor_description.name
        self._type = sensor_description.key
        self._unique_id = unique_id
        self._data = coordinator.data
        self.coordinator = coordinator
        self._state = None
        self._icon = sensor_description.icon
        self._min_version = sensor_description.min_version

        self._attr_name = f"{self._config.data[CONF_NAME]} {self._name}"
        self._attr_unique_id = f"{self._name}_{self._unique_id}"

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
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._type)

    @property
    def icon(self) -> str | None:
        """Return the icon."""
        # Dynamic icon for the 'state' sensor
        if self._type == "state":
            state_val = self.native_value
            return STATUS_ICONS.get(state_val, "mdi:alert-octagon")

        return self.entity_description.icon

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if not self.coordinator.last_update_success:
            return False

        data = self.coordinator.data
        if data is None or self._type not in data:
            return False

        # Check firmware version requirement
        manager = self.hass.data[DOMAIN][self._unique_id][MANAGER]
        if self._min_version and not manager.version_check(self._min_version):
            return False

        return True
