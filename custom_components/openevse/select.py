"""Support for OpenEVSE controls using the select platform."""
from __future__ import annotations
import logging
from typing import Any, Optional

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import connect, send_command
from .const import COORDINATOR, DOMAIN, SELECT_TYPES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the OpenEVSE selects."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    manager = hass.data[DOMAIN][entry.entry_id][MANAGER]
    selects = []
    for select in SELECT_TYPES:
        selects.append(OpenEVSESelect(hass, entry, coordinator, select, manager))

    async_add_entities(selects, False)


class OpenEVSESelect(CoordinatorEntity, SelectEntity):
    """Define OpenEVSE Service Level select."""

    def __init__(
        self,
        hass,
        config_entry: ConfigEntry,
        coordinator: OpenEVSEUpdateCoordinator,
        name: str,
        manager: OpenEVSEManager,
    ) -> None:
        super().__init__(coordinator)
        self.hass = hass
        self._config = config_entry
        self.coordinator = coordinator
        self._type = name
        self._attr_name = f"{config_entry.data[CONF_NAME]} {SELECT_TYPES[name][0]}"
        self._attr_unique_id = f"{self._attr_name}_{config_entry.entry_id}"
        self._attr_current_option = self.coordinator.data[self._type]
        self._attr_options = self.get_options()
        self._command = SELECT_TYPES[name][2]
        self._manager = manager
        self._entity_category = SELECT_TYPES[name][3]

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
        return str(self.coordinator.data[self._type])

    async def async_select_option(self, option: Any) -> None:
        """Change the selected option."""
        charger = self._manager
        command = f"{self._command} {option}"
        _LOGGER.debug("Command: %s", command)
        try:
            await send_command(charger, command)
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
        return self.coordinator.last_update_success

    @property
    def entity_category(self) -> str | None:
        """Return the category of the entity, if any."""
        return self._entity_category

    def get_options(self) -> list[str]:
        """Return a set of selectable options."""
        if self._type == "current_capacity":
            min = self.coordinator.data["min_amps"]
            max = self.coordinator.data["max_amps"]
            return list([item for item in range(min, max + 1)])
        return SELECT_TYPES[self._type][2]
