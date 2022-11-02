"""Support for OpenEVSE switches."""
from __future__ import annotations

import logging
from typing import Any, cast

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME

from . import (
    CommandFailed,
    InvalidValue,
    OpenEVSEManager,
    OpenEVSEUpdateCoordinator,
    send_command,
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
        switches.append(
            OpenEVSESwitch(hass, entry, coordinator, SWITCH_TYPES[switch], manager)
        )

    async_add_entities(switches, False)


class OpenEVSESwitch(CoordinatorEntity, SwitchEntity):
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
        self._unique_id = config_entry.entry_id
        self._attr_name = f"{config_entry.data[CONF_NAME]} {description.name}"
        self._attr_unique_id = f"{self._attr_name}_{config_entry.entry_id}"
        self._manager = manager
        self._state = None
        self.toggle_command = description.toggle_command

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
            "connections": {(DOMAIN, self._unique_id)},
        }

        return info

    @property
    def is_on(self) -> bool:
        """Return True if switch is on."""
        data = self.coordinator.data
        if self._type not in data.keys():
            _LOGGER.info("switch [%s] not supported.", self._type)
            return None
        _LOGGER.debug("switch [%s]: %s", self._attr_name, data[self._type])
        if self._type == "state":
            return True if data[self._type] == "Sleeping" else False
        return cast(bool, data[self._type] == 1)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        if self.toggle_command is not None:
            await getattr(self._manager, self.toggle_command)()
        else:
            return

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        if self.toggle_command is not None:
            await getattr(self._manager, self.toggle_command)()
        else:
            return
