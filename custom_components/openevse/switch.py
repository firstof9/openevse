"""Support for OpenEVSE switches."""
import logging
from typing import Any, cast

from homeassistant.components.switch import (
    SwitchEntity, 
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME

from . import (
    send_command,
    CommandFailed,
    InvalidValue,
    OpenEVSEManager,
    OpenEVSEUpdateCoordinator,
)
from .const import COORDINATOR, DOMAIN, MANAGER, SWITCH_TYPES
from .entity import OpenEVSESwitchEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the OpenEVSE switches."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    manager = hass.data[DOMAIN][entry.entry_id][MANAGER]

    switches = []
    for switch in SWITCH_TYPES:
        switches.append(OpenEVSESwitch(hass, entry, coordinator, SWITCH_TYPES[switch], manager))

    async_add_entities(switches, False)


class OpenEVSESwitch(SwitchEntity):
    """Representation of the value of a OpenEVSE Switch."""

    def __init__(
        self,
        hass,
        config_entry: ConfigEntry,
        coordinator: OpenEVSEUpdateCoordinator,
        description: OpenEVSESwitchEntityDescription,
        manager: OpenEVSEManager,
    ) -> None:
        super().__init__(coordinator)    
        self.hass = hass
        self._config = config_entry
        self.coordinator = coordinator
        self._type = description.key
        self._attr_name = f"{config_entry.data[CONF_NAME]} {description.name}"
        self._attr_unique_id = f"{self._attr_name}_{config_entry.entry_id}"
        self._manager = manager
        self._state = None
        self.on_command = description.on_command | None
        self.off_command = description.off_command | None
        self.toggle_command = description.toggle_command | None


    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return f"{self._attr_name}_{self._attr_unique_id}"

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._attr_name

    @property
    def device_info(self) -> dict:
        """Return a port description for device registry."""
        info = {
            "manufacturer": "OpenEVSE",
            "name": self._config.data[CONF_NAME],
            "connections": {(DOMAIN, self._attr_unique_id)},
        }

        return info

    @property
    def is_on(self) -> bool:
        """Return True if switch is on."""
        data = self.coordinator.data
        if self._type not in data.keys():
            _LOGGER.info("switch [%s] not supported.")
            return None
        _LOGGER.debug("switch [%s]: %s", self._attr_name, data[self._type])
        if self._type == "state":
            return True if data[self._type] == "sleeping" else False
        return cast(bool, data[self._type] == 1)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        if self.on_command is not None:
            try:
                await send_command(self._manager, self.on_command)
            except (ValueError, KeyError):
                    _LOGGER.warning("Could not set status for %s", self._attr_name)     
            except InvalidValue:
                _LOGGER.error(f"Value {self.on_command} invalid for switch.")
            except CommandFailed:
                _LOGGER.error("Switch command failed.")                               
        elif self.toggle_command is not None:
            await getattr(self._manager, self.toggle_command)
        else:
            return

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        if self.off_command is not None:
            try:
                await send_command(self._manager, self.off_command)
            except (ValueError, KeyError):
                    _LOGGER.warning("Could not set status for %s", self._attr_name)                    
            except InvalidValue:
                _LOGGER.error(f"Value {self.off_command} invalid for switch.")
            except CommandFailed:
                _LOGGER.error("Switch command failed.")                     
        elif self.toggle_command is not None:
            await getattr(self._manager, self.toggle_command)
        else:
            return
