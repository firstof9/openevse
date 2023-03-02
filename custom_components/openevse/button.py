"""Support for OpenEVSE buttons."""
from __future__ import annotations

import logging

from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import OpenEVSEManager
from .const import BUTTON_TYPES, CONF_NAME, DOMAIN, MANAGER

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenEVSE buttons based on a config entry."""
    manager = hass.data[DOMAIN][config_entry.entry_id][MANAGER]
    assert manager is not None
    buttons = []
    for button in BUTTON_TYPES:  # pylint: disable=consider-using-dict-items
        buttons.append(OpenEVSEButton(BUTTON_TYPES[button], manager, config_entry))
    async_add_entities(buttons, False)


class OpenEVSEButton(ButtonEntity):
    """OpenEVSE restart button."""

    def __init__(
        self,
        button_description: ButtonEntityDescription,
        manager: OpenEVSEManager,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialise a OpenEVSE button."""
        self.entity_description = button_description
        self.config = config_entry
        self.manager = manager
        self._key = button_description.key
        self._name = button_description.name
        self._base_unique_id = config_entry.entry_id
        self._attr_name = f"{config_entry.data[CONF_NAME]} {self._name}"
        self._attr_unique_id = f"{self._base_unique_id}.{self._key}"

    @property
    def device_info(self) -> dict:
        """Return a port description for device registry."""
        info = {
            "manufacturer": "OpenEVSE",
            "name": self.config.data[CONF_NAME],
            "connections": {(DOMAIN, self._base_unique_id)},
        }

        return info

    async def async_press(self) -> None:
        """Press the button."""
        await getattr(self.manager, self._key)()
