"""Support for OpenEVSE controls using the select platform."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import (
    CommandFailedError,
    InvalidValueError,
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
    for select in SELECT_TYPES:  # pylint: disable=consider-using-dict-items
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
        """Initialize."""
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
        self._min_version = description.min_version

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

        if self._type == "override_state":
            if option != "auto":
                response = await charger.set_override(state=option.lower())
                _LOGGER.debug("Select response: %s", response)
            else:
                response = await charger.clear_override()
                _LOGGER.debug("Select Auto response: %s", response)
            return None

        try:
            if self._command.startswith("$"):
                command = f"{self._command} {option}"
                _LOGGER.debug("Command: %s", command)
                await send_command(charger, command)
            else:
                _LOGGER.debug("Command: %s Option: %s", self._command, option)
                await getattr(self._manager, self._command)(option)
        except (ValueError, KeyError) as err:
            _LOGGER.warning(
                "Could not set status for %s error: %s", self._attr_name, err
            )
        except InvalidValueError:
            _LOGGER.error("Value %s invalid for command %s.", option, self._command)
        except CommandFailedError:
            _LOGGER.error("Command %s failed.", self._command)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        data = self.coordinator.data
        manager = self.hass.data[DOMAIN][self._config.entry_id][MANAGER]
        attributes = ("divertmode", "divert_active")
        if (
            set(attributes).issubset(data.keys())
            and self._type == "max_current_soft"
            and data["divert_active"]
            and data["divertmode"] == "eco"
        ):
            _LOGGER.debug(
                "Disabling %s due to PV Divert being active.", self._attr_name
            )
            return False
        if self._min_version and not manager.version_check(self._min_version):
            return False
        return self.coordinator.last_update_success

    def get_options(self) -> list[str]:
        """Return a set of selectable options."""
        if self._type == "max_current_soft":
            amps_min = self.coordinator.data["min_amps"]
            amps_max = self.coordinator.data["max_amps"] + 1
            # pylint: disable-next=consider-using-generator
            options = [str(item) for item in range(amps_min, amps_max)]
            _LOGGER.debug("Max Amps: %s", options)
            return options
        return self._default_options
