"""Support for OpenEVSE controls using the light platform."""

from __future__ import annotations

import logging
from typing import Any, ClassVar

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import (
    CONNECTION_ERRORS,
    OpenEVSEManager,
    OpenEVSEUpdateCoordinator,
)
from .const import (
    CONF_NAME,
    CONNECTION_ERROR,
    COORDINATOR,
    DOMAIN,
    LIGHT_TYPES,
    MANAGER,
)
from .entity import OpenEVSELightEntityDescription

_LOGGER = logging.getLogger(__name__)
DEFAULT_ON = 125
DEFAULT_OFF = 0


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenEVSE Number entity from Config Entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    manager = hass.data[DOMAIN][config_entry.entry_id][MANAGER]

    entities: list[LightEntity] = []

    for light in LIGHT_TYPES:
        if LIGHT_TYPES[light].key in coordinator.data:
            entities.append(
                OpenEVSELight(config_entry, coordinator, LIGHT_TYPES[light], manager)
            )
    async_add_entities(entities)


class OpenEVSELight(CoordinatorEntity, LightEntity):
    """Implementation of an OpenEVSE light."""

    _attr_supported_color_modes: ClassVar[set[ColorMode]] = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS

    def __init__(
        self,
        config: ConfigEntry,
        coordinator: OpenEVSEUpdateCoordinator,
        light_description: OpenEVSELightEntityDescription,
        manager: OpenEVSEManager,
    ) -> None:
        """Initialize the light."""
        super().__init__(coordinator)
        self._config = config
        self.entity_description = light_description
        self._name = light_description.name
        self._type = light_description.key
        self._unique_id = config.entry_id
        self._command = light_description.command
        self._data = coordinator.data
        self.coordinator = coordinator
        self.manager = manager
        self._min_version = light_description.min_version

        self._attr_name = f"{self._config.data[CONF_NAME]} {self._name}"
        self._attr_unique_id = f"{self._name}_{self._unique_id}"
        data = coordinator.data
        if isinstance(data, dict) and self._type in data:
            self._attr_brightness = data[self._type]
        else:
            self._attr_brightness = None

    @property
    def device_info(self) -> dict:
        """Return a port description for device registry."""
        info = {
            "manufacturer": "OpenEVSE",
            "name": self._config.data[CONF_NAME],
            "connections": {(DOMAIN, self._unique_id)},
        }

        return info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data = self.coordinator.data
        if isinstance(data, dict) and self._type in data:
            self._attr_brightness = data[self._type]
        else:
            self._attr_brightness = None
        self.async_write_ha_state()

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        return self._attr_brightness

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        if self.brightness is None:
            return None
        return bool(self.brightness != 0)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS, self.brightness)

        try:
            if ATTR_BRIGHTNESS in kwargs:
                await self.manager.set_led_brightness(brightness)
                return
            await self.manager.set_led_brightness(DEFAULT_ON)
        except CONNECTION_ERRORS as err:
            _LOGGER.error(CONNECTION_ERROR, err)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        try:
            await self.manager.set_led_brightness(DEFAULT_OFF)
        except CONNECTION_ERRORS as err:
            _LOGGER.error(CONNECTION_ERROR, err)
