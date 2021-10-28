"""Binary sensors for OpenEVSE Charger."""
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_NAME, COORDINATOR, DOMAIN, BINARY_SENSORS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    binary_sensors = []
    for binary_sensor in BINARY_SENSORS:
        binary_sensors.append(
            OpenEVSEBinarySensor(BINARY_SENSORS[binary_sensor], coordinator, entry)
        )

    async_add_devices(binary_sensors, False)


class OpenEVSEBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Implementation of an OpenEVSE binary sensor."""

    def __init__(
        self,
        sensor_description: BinarySensorEntityDescription,
        coordinator: str,
        config: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config = config
        self.entity_description = sensor_description
        self._name = sensor_description.name
        self._type = sensor_description.key
        self._unique_id = config.entry_id

        self._attr_name = f"{self._config.data[CONF_NAME]}_{self._name}"
        self._attr_unique_id = f"{self._name}_{self._unique_id}"
        self._attr_is_on = coordinator.data.get(self._type)

    @property
    def device_info(self) -> dict:
        """Return a port description for device registry."""
        info = {
            "manufacturer": "OpenEVSE",
            "name": self._config.data[CONF_NAME],
            "connections": {(DOMAIN, self._unique_id)},
        }

        return info
