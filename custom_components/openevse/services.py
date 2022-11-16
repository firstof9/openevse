"""Services for OpenEVSE."""
from __future__ import annotations
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import async_get as async_get_device_registry

from .const import (
    DOMAIN,
    MANAGER,
    ATTR_DEVICE_ID,
    ATTR_STATE,
    ATTR_CHARGE_CURRENT,
    ATTR_MAX_CURRENT,
    ATTR_ENERGY_LIMIT,
    ATTR_TIME_LIMIT,
    ATTR_AUTO_RELEASE,
)

_LOGGER = logging.getLogger(__name__)


async def set_overrride(
    hass: HomeAssistant,
    data: dict,
    config_entry: ConfigEntry,
) -> None:
    """Set the override."""
    if ATTR_DEVICE_ID in data:
        device_id = data[ATTR_DEVICE_ID]
        _LOGGER.debug("Device ID: %s", device_id)
    else:
        raise ValueError
    manager = hass.data[DOMAIN][config_entry.entry_id][MANAGER]

    if ATTR_STATE in data:
        state = data[ATTR_STATE]
    else:
        _LOGGER.error("Missing state value!")
        raise ValueError

    if ATTR_CHARGE_CURRENT in data:
        charge_current = data[ATTR_CHARGE_CURRENT]
    else:
        charge_current = None
    if ATTR_MAX_CURRENT in data:
        max_current = data[ATTR_MAX_CURRENT]
    else:
        max_current = None
    if ATTR_ENERGY_LIMIT in data:
        energy_limit = data[ATTR_ENERGY_LIMIT]
    else:
        energy_limit = None
    if ATTR_TIME_LIMIT in data:
        time_limit = data[ATTR_TIME_LIMIT]
    else:
        time_limit = None
    if ATTR_AUTO_RELEASE in data:
        auto_release = data[ATTR_AUTO_RELEASE]
    else:
        auto_release = None

    response = await manager.set_override(
        state=state,
        charge_current=charge_current,
        max_current=max_current,
        energy_limit=energy_limit,
        time_limit=time_limit,
        auto_release=auto_release,
    )
    _LOGGER.debug("Set Override response: %s", response)
    return


async def clear_override(
    hass: HomeAssistant,
    data: str,
    config_entry: ConfigEntry,
) -> None:
    """Clear the manual override."""
    _LOGGER.debug("Clear Override data: %s", data)
    manager = hass.data[DOMAIN][config_entry.entry_id][MANAGER]

    await manager.clear_override()
    _LOGGER.debug("Override clear command sent.")
