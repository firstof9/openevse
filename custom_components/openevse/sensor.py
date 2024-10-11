"""Support for monitoring an OpenEVSE Charger."""

from __future__ import annotations

import logging
from typing import Any
from datetime import timedelta

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import CONF_NAME, COORDINATOR, DOMAIN, SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)


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
        data = self.coordinator.data
        if data is None:
            self._state = None
        if self._type in data.keys():
            value = data[self._type]
            if self._type == "charge_time_elapsed":
                self._state = value / 60
            elif self._type == "usage_total" and isinstance(value, int):
                self._state = value / 1000
            elif self._type in [
                "usage_session",
                "charging_current",
                "charging_power",
            ]:
                self._state = value / 1000
            elif self._type == "charging_voltage":
                self._state = value
            elif self.device_class == SensorDeviceClass.TIMESTAMP:
                if self._type == "vehicle_eta":
                    # Timestamp in the future
                    value = dt_util.utcnow() + timedelta(seconds=value)
                self._state = value
            else:
                self._state = value

        _LOGGER.debug("Sensor [%s] updated value: %s", self._type, self._state)
        self.update_icon()
        return self._state

    @property
    def icon(self) -> str:
        """Return the icon."""
        return self._icon

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        data = self.coordinator.data
        if self._type not in data or (self._type in data and data[self._type] is None):
            return False
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
