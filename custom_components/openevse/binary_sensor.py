"""Binary sensors for OpenEVSE Charger."""

import logging
from typing import cast

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import BINARY_SENSORS, CONF_NAME, COORDINATOR, DOMAIN
from .entity import OpenEVSEBinarySensorEntityDescription, OpenEVSEEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    binary_sensors = []
    for description in BINARY_SENSORS:
        binary_sensors.append(OpenEVSEBinarySensor(description, coordinator, entry))

    async_add_devices(binary_sensors, False)


class OpenEVSEBinarySensor(CoordinatorEntity, OpenEVSEEntity, BinarySensorEntity):
    """Implementation of an OpenEVSE binary sensor."""

    entity_description: OpenEVSEBinarySensorEntityDescription

    def __init__(
        self,
        sensor_description: OpenEVSEBinarySensorEntityDescription,
        coordinator: DataUpdateCoordinator,
        config: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._config = config
        self.entity_description = sensor_description
        self._name = sensor_description.name
        self._type = sensor_description.key
        self._unique_id = config.entry_id

        self._attr_name = f"{self._config.data[CONF_NAME]} {self._name}"
        self._attr_unique_id = f"{self._name}_{self._unique_id}"

    @property
    def is_on(self) -> bool:
        """Return True if the service is on."""
        data = self.coordinator.data
        if getattr(self.entity_description, "value_fn", None) is not None:
            return cast(bool, self.entity_description.value_fn(data) == 1)
        if self._type not in data:
            self.coordinator.logger.info(
                "binary_sensor [%s] not supported.", self._type
            )
            return None
        self.coordinator.logger.debug(
            "binary_sensor [%s]: %s", self._name, data[self._type]
        )
        return cast(bool, data[self._type] == 1)
