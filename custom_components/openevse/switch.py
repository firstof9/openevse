"""Support for OpenEVSE switches."""
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME

from . import send_command, CommandFailed, InvalidValue, OpenEVSEManager
from .const import COORDINATOR, DOMAIN, MANAGER, SWITCH_TYPES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the OpenEVSE switches."""
    manager = hass.data[DOMAIN][entry.entry_id][MANAGER]

    switches = []
    for switch in SWITCH_TYPES:
        switches.append(OpenEVSESwitch(hass, switch, entry, manager))

    async_add_entities(switches, False)


class OpenEVSESwitch(SwitchEntity):
    """Representation of the value of a OpenEVSE Switch."""

    def __init__(
        self, hass, name: str, config_entry: ConfigEntry, manager: OpenEVSEManager
    ) -> None:
        self._coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
        self.hass = hass
        self._config = config_entry
        self._name = name
        self._unique_id = config_entry.entry_id
        self._state = None
        self._manager = manager

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return f"{self._name}_{self._unique_id}"

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def device_info(self) -> dict:
        """Return a port description for device registry."""
        info = {
            "manufacturer": "OpenEVSE",
            "name": self._config.data[CONF_NAME],
            "connections": {(DOMAIN, self._unique_id)},
        }

        return info

    async def async_update(self) -> None:
        """Update the switch value."""
        self._state = await self.get_switch()

    @property
    def is_on(self) -> bool:
        """Return True if switch is on."""
        return self._state

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.set_switch(True)
        self._state = await self.get_switch()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.set_switch(False)
        self._state = await self.get_switch()

    async def get_switch(self) -> bool:
        """Get the current state of the switch."""
        charger = self._manager
        return await update_switch(charger)

    async def set_switch(self, status: bool) -> None:
        """Get the current state of the switch."""
        charger = self._manager

        try:
            if status:
                await send_command(charger, "$FS")
            else:
                await send_command(charger, "$FE")
        except (ValueError, KeyError):
            _LOGGER.warning("Could not set status for %s", self._name)
        except InvalidValue:
            _LOGGER.error(f"Value {status} invalid for switch.")
        except CommandFailed:
            _LOGGER.error("Switch command failed.")


async def update_switch(handler) -> bool:
    await handler.update()
    _LOGGER.debug("update_switch: %s", handler.state)
    state = True if handler.state == "sleeping" else False
    return state
