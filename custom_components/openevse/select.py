import logging
from typing import Optional

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_USERNAME,
    ELECTRIC_CURRENT_AMPERE,
)
from requests import RequestException

from . import connect, get_wifi_data, send_command
from .const import COORDINATOR, DOMAIN, MAX_CURRENT, SERVICE_LEVELS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the OpenEVSE selects."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    selects = []
    selects.append(OpenEVSEServiceLevelSelect(hass, entry, coordinator))
    selects.append(OpenEVSEMaxCurrentSelect(hass, entry, coordinator))

    async_add_entities(selects, False)


class OpenEVSEServiceLevelSelect(CoordinatorEntity, SelectEntity):
    """Define OpenEVSE Service Level select."""

    def __init__(self, hass, config_entry: ConfigEntry, coordinator) -> None:
        super().__init__(coordinator)
        self.hass = hass
        self._config = config_entry
        self.coordinator = coordinator
        self._attr_name = f"{config_entry.data[CONF_NAME]} Service Level"
        self._attr_unique_id = f"{self._attr_name}_{config_entry.entry_id}"
        self._attr_current_option = self.coordinator.data["service_level"]
        self._attr_options = SERVICE_LEVELS

    @property
    def device_info(self):
        """Return a port description for device registry."""
        info = {
            "manufacturer": "OpenEVSE",
            "name": self._config.data[CONF_NAME],
            "connections": {(DOMAIN, self._config.entry_id)},
        }
        return info

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        host = self._config.data.get(CONF_HOST)
        username = self._config.data.get(CONF_USERNAME)
        password = self._config.data.get(CONF_PASSWORD)
        charger = await self.hass.async_add_executor_job(
            connect, host, username, password
        )
        command = f"$SL {option}"
        try:
            await self.hass.async_add_executor_job(send_command, charger, command)
        except (RequestException, ValueError, KeyError):
            _LOGGER.warning("Could not set status for %s", self._attr_name)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success


class OpenEVSEMaxCurrentSelect(CoordinatorEntity, SelectEntity):
    """Define OpenEVSE Service Level select."""

    def __init__(self, hass, config_entry: ConfigEntry, coordinator) -> None:
        super().__init__(coordinator)
        self.hass = hass
        self._config = config_entry
        self.coordinator = coordinator
        self._attr_name = f"{config_entry.data[CONF_NAME]} Max Current"
        self._attr_unique_id = f"{self._attr_name}_{config_entry.entry_id}"
        self._attr_current_option = self.coordinator.data["max_amps"]
        self._attr_options = MAX_CURRENT
        self._unit_of_measurement = ELECTRIC_CURRENT_AMPERE

    @property
    def device_info(self):
        """Return a port description for device registry."""
        info = {
            "manufacturer": "OpenEVSE",
            "name": self._config.data[CONF_NAME],
            "connections": {(DOMAIN, self._config.entry_id)},
        }
        return info

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        host = self._config.data.get(CONF_HOST)
        username = self._config.data.get(CONF_USERNAME)
        password = self._config.data.get(CONF_PASSWORD)
        charger = await self.hass.async_add_executor_job(
            connect, host, username, password
        )
        command = f"$SC {int(option)}"
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
