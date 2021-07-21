"""Support for OpenEVSE switches."""
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_USERNAME,
    CONF_PASSWORD,
    STATE_ON,
)
import openevsewifi
from requests import RequestException
from typing import Any

from .const import SWITCH_TYPES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the OpenEVSE switches."""

    switches = []
    for switch in SWITCH_TYPES:
        switches.append(OpenEVSESwitch(hass, switch, entry))

    async_add_entities(switches, False)


class OpenEVSESwitch(SwitchEntity):
    """Representation of the value of a OpenEVSE Switch."""

    def __init__(self, hass, name, config_entry: ConfigEntry) -> None:
        self.hass = hass
        self._config = config_entry
        self._name = name
        self._unique_id = config_entry.entry_id
        self._state = None

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return f"{self._name}_{self._unique_id}"

    @property
    def name(self):
        """Return the name of the entity."""
        return self._name

    async def async_update(self):
        """Update the switch value."""
        self._state = await self.get_switch()

    @property
    def is_on(self) -> bool:
        """Return True if switch is on."""
        return self._state == STATE_ON

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.set_switch(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.set_switch(False)

    async def get_switch(self) -> bool:
        """ Get the current state of the switch."""
        host = self._config.data.get(CONF_HOST)
        username = self._config.data.get(CONF_USERNAME)
        password = self._config.data.get(CONF_PASSWORD)
        charger = openevsewifi.Charger(host, username=username, password=password)
        status = await self.hass.async_add_executor_job(send_command, charger, "$GS")
        _LOGGER.warning("DEBUG: %s", status)

        try:
            if status == 254:
                return True
            return False
        except (RequestException, ValueError, KeyError):
            _LOGGER.warning("Could not update status for %s", self._name)

    async def set_switch(self, status: bool) -> None:
        """ Get the current state of the switch."""
        host = self._config.data.get(CONF_HOST)
        username = self._config.data.get(CONF_USERNAME)
        password = self._config.data.get(CONF_PASSWORD)
        charger = await self.hass.async_add_executor_job(
            connect, host, username, password
        )

        try:
            if status:
                await self.hass.async_add_executor_job(send_command, charger, "$FS")
            else:
                await self.hass.async_add_executor_job(send_command, charger, "$FE")
        except (RequestException, ValueError, KeyError):
            _LOGGER.warning("Could not set status for %s", self._name)


def connect(host: str, username: str = None, password: str = None) -> Any:
    return openevsewifi.Charger(host, username=username, password=password)


def send_command(handler, command) -> Any:
    response = handler._send_command(command)
    _LOGGER.warning("DEBUG: %s", response)
    return response


def get_status(handler) -> Any:
    status = handler.status
    return status
