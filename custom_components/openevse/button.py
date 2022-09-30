"""Support for OpenEVSE buttons."""
from __future__ import annotations
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import OpenEVSEManager
from .const import CONF_NAME, DOMAIN, MANAGER

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up OpenEVSE buttons based on a config entry."""

    manager = hass.data[DOMAIN][config_entry.entry_id][MANAGER]

    @callback
    def async_add_restart_button_entity() -> None:
        """Add restart button entity."""
        assert manager is not None 
        async_add_entities([OpenEVSEResetButton(manager, config_entry)])

    config_entry.async_on_unload(
        async_dispatcher_connect(
            hass,
            f"{DOMAIN}_{config_entry.entry_id}_add_restart_button_entity",
            async_add_restart_button_entity,
        )
    )        


class OpenEVSEResetButton(ButtonEntity):
    """Implementation of an OpenEVSE button."""

    _attr_should_poll = False
    _attr_entity_category = EntityCategory.CONFIG
    _attr_has_entity_name = True    


    def __init__(self, manager: OpenEVSEManager, config_entry: ConfigEntry) -> None:
        """Initialize a restart button entity."""

        # Entity class attributes
        self._attr_name = "Restart"
        self._config = config_entry
        self._manager = manager
        self._base_unique_id = config_entry.entry_id
        self._attr_unique_id = f"{self._base_unique_id}.restart"

    @property
    def device_info(self) -> dict:
        """Return a port description for device registry."""
        info = {
            "manufacturer": "OpenEVSE",
            "name": self._config.data[CONF_NAME],
            "connections": {(DOMAIN, self._base_unique_id)},
        }

        return info

    async def async_press(self) -> None:
        """Press the button."""
        self.hass.async_create_task(self._manager.restart_wifi())