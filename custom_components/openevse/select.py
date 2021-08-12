import logging
from typing import Any, Optional

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from requests import RequestException

from . import connect, send_command
from .const import COORDINATOR, DOMAIN, SELECT_TYPES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the OpenEVSE selects."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    selects = []
    for select in SELECT_TYPES:
        selects.append(OpenEVSESelect(hass, entry, coordinator, select))

    async_add_entities(selects, False)


class OpenEVSESelect(CoordinatorEntity, SelectEntity):
    """Define OpenEVSE Service Level select."""

    def __init__(self, hass, config_entry: ConfigEntry, coordinator, name: str) -> None:
        super().__init__(coordinator)
        self.hass = hass
        self._config = config_entry
        self.coordinator = coordinator
        self._type = name
        self._attr_name = f"{config_entry.data[CONF_NAME]} {SELECT_TYPES[name][0]}"
        self._attr_unique_id = f"{self._attr_name}_{config_entry.entry_id}"
        self._attr_current_option = self.coordinator.data[name]
        self._attr_options = self.get_options()
        self._command = SELECT_TYPES[name][3]
        self._unit_of_measurement = SELECT_TYPES[name][1]

    @property
    def device_info(self):
        """Return a port description for device registry."""
        info = {
            "manufacturer": "OpenEVSE",
            "name": self._config.data[CONF_NAME],
            "connections": {(DOMAIN, self._config.entry_id)},
        }
        return info

    async def async_select_option(self, option: Any) -> None:
        """Change the selected option."""
        host = self._config.data.get(CONF_HOST)
        username = self._config.data.get(CONF_USERNAME)
        password = self._config.data.get(CONF_PASSWORD)
        charger = await self.hass.async_add_executor_job(
            connect, host, username, password
        )
        command = f"{self._command} {option}"
        try:
            await self.hass.async_add_executor_job(send_command, charger, command)
        except (RequestException, ValueError, KeyError):
            _LOGGER.warning("Could not set status for %s", self._attr_name)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def unit_of_measurement(self) -> Optional[str]:
        """Return the unit of measurement of this sensor."""
        return self._unit_of_measurement

    def get_options(self) -> list:
        if self._type == "current_capacity":
            min = self.coordinator.data["min_amps"]
            max = self.coordinator.data["max_amps"]
            return [item for item in range(min, max + 1)]
        return SELECT_TYPES[self._type][2]
