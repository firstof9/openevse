"""Support for OpenEVSE controls using the select platform."""
from __future__ import annotations

import logging
from typing import Any, Optional

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import (
    CommandFailed,
    InvalidValue,
    OpenEVSEManager,
    OpenEVSEUpdateCoordinator,
    send_command,
)
from .const import COORDINATOR, DOMAIN, MANAGER, SELECT_TYPES
from .entity import OpenEVSESelectEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the OpenEVSE selects."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    manager = hass.data[DOMAIN][entry.entry_id][MANAGER]
    selects = []
    for select in SELECT_TYPES:
        selects.append(
            OpenEVSESelect(hass, entry, coordinator, SELECT_TYPES[select], manager)
        )

    async_add_entities(selects, False)


class OpenEVSESelect(CoordinatorEntity, SelectEntity):
    """Define OpenEVSE Service Level select."""

    def __init__(
        self,
        hass,
        config_entry: ConfigEntry,
        coordinator: OpenEVSEUpdateCoordinator,
        description: OpenEVSESelectEntityDescription,
        manager: OpenEVSEManager,
    ) -> None:
        super().__init__(coordinator)
        self.hass = hass
        self._config = config_entry
        self.coordinator = coordinator
        self._type = description.key
        self._attr_name = f"{config_entry.data[CONF_NAME]} {description.name}"
        self._attr_unique_id = f"{self._attr_name}_{config_entry.entry_id}"
        self._command = description.command
        self._manager = manager
        self._default_options = description.default_options
        self._attr_options = self.get_options()

    @property
    def device_info(self):
        """Return a port description for device registry."""
        info = {
            "manufacturer": "OpenEVSE",
            "name": self._config.data[CONF_NAME],
            "connections": {(DOMAIN, self._config.entry_id)},
        }
        return info

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        data = self.coordinator.data
        if self._type in data and data is not None:
            state = data[self._type]
            _LOGGER.debug("Select [%s] updated value: %s", self._type, state)
            return str(state)
        return None

    async def async_select_option(self, option: Any) -> None:
        """Change the selected option."""
        charger = self._manager

        try:
            if self._command.startswith("$"):
                command = f"{self._command} {option}"
                _LOGGER.debug("Command: %s", command)
                await send_command(charger, command)
            else:
                await getattr(self._manager, self._command)(option)
        except (ValueError, KeyError) as err:
            _LOGGER.warning(
                "Could not set status for %s error: %s", self._attr_name, err
            )
        except InvalidValue:
            _LOGGER.error(f"Value {option} invalid for command {self._command}.")
        except CommandFailed:
            _LOGGER.error(f"Command {self._command} failed.")

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if self._type not in self.coordinator.data:
            return False
        return self.coordinator.last_update_success

    def get_options(self) -> list[str]:
        """Return a set of selectable options."""
        if self._type == "max_current_soft":
            min = self.coordinator.data["min_amps"]
            max = self.coordinator.data["max_amps"]
            _LOGGER.debug(
                "Max Amps: %s", list([str(item) for item in range(min, max + 1)])
            )
            return list([str(item) for item in range(min, max + 1)])
        return self._default_options
