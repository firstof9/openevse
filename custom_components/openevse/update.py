"""Support for OpenEVSE updates."""
from __future__ import annotations

import logging

from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntity,
    UpdateEntityFeature,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from . import OpenEVSEManager
from .const import CONF_NAME, COORDINATOR, DOMAIN, FW_COORDINATOR, MANAGER

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up update entities for Netgear component."""
    manager = hass.data[DOMAIN][entry.entry_id][MANAGER]
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    fw_coordinator = hass.data[DOMAIN][entry.entry_id][FW_COORDINATOR]
    entities = [OpenEVSEUpdateEntity(coordinator, fw_coordinator, manager, entry)]

    async_add_entities(entities)


class OpenEVSEUpdateEntity(CoordinatorEntity, UpdateEntity):
    """Update entity for a OpenEVSE device."""

    _attr_device_class = UpdateDeviceClass.FIRMWARE
    _attr_supported_features = UpdateEntityFeature.RELEASE_NOTES

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        fw_coordinator: DataUpdateCoordinator,
        manager: OpenEVSEManager,
        config: ConfigEntry,
    ) -> None:
        """Initialize a OpenEVSE device."""
        super().__init__(fw_coordinator)
        self.fw_coordinator = fw_coordinator
        self.coordinator = coordinator
        self.config = config
        self._attr_name = f"{config.data[CONF_NAME]} Update"
        self._base_unique_id = config.entry_id
        self._attr_unique_id = f"{self._base_unique_id}.update"

    @property
    def device_info(self) -> dict:
        """Return a port description for device registry."""
        info = {
            "manufacturer": "OpenEVSE",
            "name": self.config.data[CONF_NAME],
            "connections": {(DOMAIN, self._base_unique_id)},
        }

        return info

    @property
    def installed_version(self) -> str | None:
        """Version currently in use."""
        if self.coordinator.data is not None:
            return self.coordinator.data.get("wifi_firmware")
        return None

    @property
    def latest_version(self) -> str | None:
        """Latest version available for install."""
        if self.fw_coordinator.data is not None:
            new_version = self.fw_coordinator.data.get("latest_version")
            if new_version is not None and self.installed_version is not None and not new_version.startswith(
                self.installed_version
            ):
                return new_version
        return self.installed_version

    @property
    def release_summary(self) -> str | None:
        """Release summary."""
        if self.fw_coordinator.data is not None:
            return self.fw_coordinator.data.get("release_summary")
        return None
