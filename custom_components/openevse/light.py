"""Support for OpenEVSE controls using the light platform."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_NAME, COORDINATOR, DOMAIN, LIGHT_TYPES, MANAGER
from .entity import OpenEVSELightEntityDescription

from . import (
    OpenEVSEManager,
    OpenEVSEUpdateCoordinator,
)

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

    for light in LIGHT_TYPES:  # pylint: disable=consider-using-dict-items
        if LIGHT_TYPES[light].key in coordinator.data:
            entities.append(
                OpenEVSELight(config_entry, coordinator, LIGHT_TYPES[light], manager)
            )
    async_add_entities(entities)


class OpenEVSELight(CoordinatorEntity, LightEntity):
    """Implementation of an OpenEVSE light."""

    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS

    def __init__(
        self,
        config: ConfigEntry,
        coordinator: OpenEVSEUpdateCoordinator,
        light_description: OpenEVSELightEntityDescription,
        manager: OpenEVSEManager,
    ) -> None:
        """Initialize the sensor."""
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
        self._attr_brightness = coordinator.data[self._type]

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
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        self._attr_brightness = self.coordinator.data[self._type]
        return self._attr_brightness

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return bool(self._attr_brightness != 0)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS, self.brightness)

        if ATTR_BRIGHTNESS in kwargs:
            await self.manager.set_led_brightness(brightness)
            return
        await self.manager.set_led_brightness(DEFAULT_ON)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        await self.manager.set_led_brightness(DEFAULT_OFF)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        manager = self.hass.data[DOMAIN][self._unique_id][MANAGER]
        if self._min_version and not manager._version_check(self._min_version):
            return False
        return True