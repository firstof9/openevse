"""Support for OpenEVSE buttons."""
from __future__ import annotations
import logging

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import OpenEVSEManager
from .const import CONF_NAME, DOMAIN, MANAGER

RESTART_BUTTON_DESCRIPTION = ButtonEntityDescription(
    key="restart",
    name="Restart",
    device_class=ButtonDeviceClass.RESTART,
    entity_category=EntityCategory.CONFIG,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenEVSE buttons based on a config entry."""

    manager = hass.data[DOMAIN][config_entry.entry_id][MANAGER]

    assert manager is not None
    async_add_entities([OpenEVSEResetButton(manager, config_entry)])


class OpenEVSEResetButton(ButtonEntity):
    """OpenEVSE restart button."""

    entity_description = RESTART_BUTTON_DESCRIPTION
    _attr_has_entity_name: bool = True

    def __init__(self, manager: OpenEVSEManager, config_entry: ConfigEntry) -> None:
        """Initialise a LIFX button."""
        self.config = config_entry
        self.manager = manager
        self._base_unique_id = config_entry.entry_id
        self._attr_unique_id = f"{self._base_unique_id}.restart"

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
        await self.manager.restart_wifi()
