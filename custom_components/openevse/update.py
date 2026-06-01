"""Support for OpenEVSE updates."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntity,
    UpdateEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from openevsehttp.__main__ import OpenEVSE

from .const import CONF_NAME, COORDINATOR, DOMAIN, FW_COORDINATOR, MANAGER

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up update entities for Netgear component."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    fw_coordinator = hass.data[DOMAIN][entry.entry_id][FW_COORDINATOR]
    manager = hass.data[DOMAIN][entry.entry_id][MANAGER]
    entities = [OpenEVSEUpdateEntity(coordinator, fw_coordinator, entry, manager)]

    async_add_entities(entities)


class OpenEVSEUpdateEntity(CoordinatorEntity, UpdateEntity):
    """Update entity for a OpenEVSE device."""

    _attr_device_class = UpdateDeviceClass.FIRMWARE
    _attr_supported_features = (
        UpdateEntityFeature.RELEASE_NOTES
        | UpdateEntityFeature.INSTALL
        | UpdateEntityFeature.PROGRESS
    )

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        fw_coordinator: DataUpdateCoordinator,
        config: ConfigEntry,
        manager: OpenEVSE,
    ) -> None:
        """Initialize a OpenEVSE device."""
        super().__init__(fw_coordinator)
        self.fw_coordinator = fw_coordinator
        self.coordinator = coordinator
        self.config = config
        self._attr_name = f"{config.data[CONF_NAME]} Update"
        self._base_unique_id = config.entry_id
        self._attr_unique_id = f"{self._base_unique_id}.update"
        self._manager = manager

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

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
            if (
                new_version is not None
                and self.installed_version is not None
                and not new_version.startswith(self.installed_version)
            ):
                return new_version
        return self.installed_version

    def release_notes(self) -> str | None:
        """Release notes."""
        return self.fw_coordinator.data.get("release_notes", None)

    @property
    def release_url(self) -> str | None:
        """Release URL."""
        if self.fw_coordinator.data is not None:
            return self.fw_coordinator.data.get("release_url")
        return None

    @property
    def in_progress(self) -> bool:
        """Update installation progress."""
        return self._manager.ota_update

    @property
    def update_percentage(self) -> int | None:
        """Update installation progress percentage."""
        return self._manager.ota_progress

    async def async_install(
        self, version: str | None, backup: bool, **kwargs: Any
    ) -> None:
        """Install an update."""
        firmware_url = (
            self.fw_coordinator.data.get("browser_download_url")
            if self.fw_coordinator.data
            else None
        )
        if not firmware_url:
            raise HomeAssistantError("No firmware download URL available to install")

        try:
            await self._manager.update_firmware(firmware_url=firmware_url)
        except Exception as err:
            raise HomeAssistantError(
                f"Failed to install firmware update: {err}"
            ) from err
