"""Support for monitoring an OpenEVSE Charger."""
import logging

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import CONF_NAME, COORDINATOR, DOMAIN, SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the OpenEVSE sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    unique_id = entry.entry_id

    sensors = []
    for sensor in SENSOR_TYPES:
        sensors.append(OpenEVSESensor(sensor, unique_id, coordinator, entry))

    async_add_entities(sensors, False)


class OpenEVSESensor(CoordinatorEntity):
    """Implementation of an OpenEVSE sensor."""

    def __init__(self, sensor_type, unique_id, coordinator, config):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config = config
        self._name = SENSOR_TYPES[sensor_type][0]
        self._type = sensor_type
        self._state = None
        self._unit_of_measurement = SENSOR_TYPES[sensor_type][1]
        self._icon = SENSOR_TYPES[sensor_type][3]
        self._unique_id = unique_id
        self._data = coordinator.data
        self.coordinator = coordinator

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return f"{self._name}_{self._unique_id}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._config.data[CONF_NAME]}_{self._name}"

    @property
    def device_info(self):
        """Return a port description for device registry."""
        info = {
            "manufacturer": "OpenEVSE",
            "name": self._config.data[CONF_NAME],
            "connections": {(DOMAIN, self._unique_id)},
        }

        return info

    @property
    def state(self):
        """Return the state of the sensor."""
        data = self.coordinator.data
        if data is None:
            return None
        if self._type in data.keys():
            if self._type == "charge_time":
                return data[self._type] / 60
            elif self._type == "usage_session":
                return round(data[self._type] / 1000, 2)
            elif self._type == "usage_total":
                return round(data[self._type] / 1000, 2)
            else:
                return data[self._type]
        return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this sensor."""
        return self._unit_of_measurement

    @property
    def icon(self) -> str:
        """Return the unit of measurement."""
        return self._icon

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
