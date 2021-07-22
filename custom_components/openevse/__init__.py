"""The openevse component."""
import asyncio
import logging
from datetime import timedelta
from typing import Any

import openevsewifi
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import Config, HomeAssistant
import homeassistant.helpers.device_registry as dr
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from requests import RequestException

from .const import (
    CONF_NAME,
    COORDINATOR,
    DOMAIN,
    ISSUE_URL,
    PLATFORMS,
    SENSOR_TYPES,
    VERSION,
)

_LOGGER = logging.getLogger(__name__)
states = {
    0: "unknown",
    1: "not connected",
    2: "connected",
    3: "charging",
    4: "vent required",
    5: "diode check failed",
    6: "gfci fault",
    7: "no ground",
    8: "stuck relay",
    9: "gfci self-test failure",
    10: "over temperature",
    254: "sleeping",
    255: "disabled",
}


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Disallow configuration via YAML."""
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up is called when Home Assistant is loading our component."""
    hass.data.setdefault(DOMAIN, {})
    _LOGGER.info(
        "Version %s is starting, if you have any issues please report" " them here: %s",
        VERSION,
        ISSUE_URL,
    )

    config_entry.add_update_listener(update_listener)
    interval = 1
    coordinator = OpenEVSEUpdateCoordinator(hass, interval, config_entry)

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    hass.data[DOMAIN][config_entry.entry_id] = {
        COORDINATOR: coordinator,
    }

    sw_version = await hass.async_add_executor_job(get_firmware, hass, config_entry)

    device_registry = await dr.async_get_registry(hass)
    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        connections={(DOMAIN, config_entry.entry_id)},
        name=config_entry.data[CONF_NAME],
        manufacturer="OpenEVSE",
        sw_version=sw_version,
    )

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, platform)
        )

    return True


def get_firmware(hass, config) -> str:
    """Get firmware version."""
    host = config.data.get(CONF_HOST)
    username = config.data.get(CONF_USERNAME)
    password = config.data.get(CONF_PASSWORD)
    charger = openevsewifi.Charger(host, username=username, password=password)

    return charger.firmware_version


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""

    _LOGGER.debug("Attempting to unload entities from the %s integration", DOMAIN)

    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config_entry, platform)
                for platform in PLATFORMS
            ]
        )
    )

    if unload_ok:
        _LOGGER.debug("Successfully removed entities from the %s integration", DOMAIN)
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Update listener."""

    _LOGGER.debug("Attempting to reload entities from the %s integration", DOMAIN)

    if config_entry.data == config_entry.options:
        _LOGGER.debug("No changes detected not reloading entities.")
        return

    new_data = config_entry.options.copy()

    hass.config_entries.async_update_entry(
        entry=config_entry,
        data=new_data,
    )

    await hass.config_entries.async_reload(config_entry.entry_id)


def get_sensors(hass, config) -> dict:

    data = {}
    host = config.data.get(CONF_HOST)
    username = config.data.get(CONF_USERNAME)
    password = config.data.get(CONF_PASSWORD)
    charger = openevsewifi.Charger(host, username=username, password=password)

    for sensor in SENSOR_TYPES:
        _sensor = {}
        try:
            sensor_property = SENSOR_TYPES[sensor][2]
            if sensor == "status" or sensor == "charge_time":
                _sensor[sensor] = workaround(charger, sensor_property)
            else:
                _sensor[sensor] = getattr(charger, sensor_property)
            _LOGGER.debug(
                "sensor: %s sensor_property: %s value: %s",
                sensor,
                sensor_property,
                _sensor[sensor],
            )
        except (RequestException, ValueError, KeyError):
            _LOGGER.warning("Could not update status for %s", sensor)
        data.update(_sensor)
    _LOGGER.debug("DEBUG: %s", data)
    return data


def workaround(handler: Any, sensor_property: str) -> Any:
    """Workaround for library issue."""
    status = handler._send_command("$GS")
    if sensor_property == "status":
        return states[int(status[1], 16)]
    elif sensor_property == "charge_time_elapsed":
        if int(status[1], 16) == 3:
            return int(status[2], 16)
        else:
            return 0


class OpenEVSEUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching mail data."""

    def __init__(self, hass, interval, config):
        """Initialize."""
        self.interval = timedelta(minutes=interval)
        self.name = f"OpenEVSE ({config.data.get(CONF_NAME)})"
        self.config = config
        self.hass = hass

        _LOGGER.debug("Data will be update every %s", self.interval)

        super().__init__(hass, _LOGGER, name=self.name, update_interval=self.interval)

    async def _async_update_data(self):
        """Fetch data"""
        try:
            data = await self.hass.async_add_executor_job(
                get_sensors, self.hass, self.config
            )
        except Exception as error:
            raise UpdateFailed(error) from error
        return data
