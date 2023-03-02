"""Provide diagnostics for openevse."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry

from .const import COORDINATOR, DOMAIN

REDACT_KEYS = {CONF_PASSWORD}


async def async_get_config_entry_diagnostics(  # pylint: disable-next=unused-argument
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    diag: dict[str, Any] = {}
    diag["config"] = config_entry.as_dict()
    return async_redact_data(diag, REDACT_KEYS)


async def async_get_device_diagnostics(  # pylint: disable-next=unused-argument
    hass: HomeAssistant, config_entry: ConfigEntry, device: DeviceEntry
) -> dict[str, Any]:
    """Return diagnostics for a device."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    return coordinator.data
