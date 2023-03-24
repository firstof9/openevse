"""The openevse component."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import Config, HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from openevsehttp.__main__ import OpenEVSE
from openevsehttp.exceptions import MissingSerial

from .const import (
    BINARY_SENSORS,
    CONF_NAME,
    COORDINATOR,
    DOMAIN,
    FW_COORDINATOR,
    ISSUE_URL,
    MANAGER,
    PLATFORMS,
    SELECT_TYPES,
    SENSOR_TYPES,
    VERSION,
)
from .services import OpenEVSEServices

_LOGGER = logging.getLogger(__name__)


async def async_setup(  # pylint: disable-next=unused-argument
    hass: HomeAssistant, config: Config
) -> bool:
    """Disallow configuration via YAML."""
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up is called when Home Assistant is loading our component."""
    hass.data.setdefault(DOMAIN, {})
    _LOGGER.info(
        "Version %s is starting, if you have any issues please report them here: %s",
        VERSION,
        ISSUE_URL,
    )

    config_entry.add_update_listener(update_listener)
    manager = OpenEVSEManager(hass, config_entry).charger
    interval = 60
    coordinator = OpenEVSEUpdateCoordinator(hass, interval, config_entry, manager)
    fw_coordinator = OpenEVSEFirmwareCheck(hass, 86400, config_entry, manager)

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()
    await fw_coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][config_entry.entry_id] = {
        COORDINATOR: coordinator,
        MANAGER: manager,
        FW_COORDINATOR: fw_coordinator,
    }

    model_info, sw_version = await get_firmware(manager)
    data = await manager.test_and_get()
    serial = data["serial"]

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        connections={(DOMAIN, config_entry.entry_id)},
        identifiers={(DOMAIN, serial)},
        name=config_entry.data[CONF_NAME],
        manufacturer="OpenEVSE",
        model=model_info,
        sw_version=sw_version,
        configuration_url=manager.url,
    )

    await coordinator.async_refresh()
    # Start the websocket listener
    manager.ws_start()

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, platform)
        )

    services = OpenEVSEServices(hass, config_entry)
    services.async_register()

    return True


async def get_firmware(manager: OpenEVSEManager) -> tuple:
    """Get firmware version."""
    _LOGGER.debug("Getting firmware versions...")
    data = {}
    try:
        await manager.update()
    except Exception as error:
        _LOGGER.error("Problem retreiving firmware data: %s", error)
        return "", ""

    try:
        data = await manager.test_and_get()
    except MissingSerial:
        _LOGGER.info("Missing serial number data, skipping...")

    if data is not None and "model" in data:
        if data["model"] != "unknown":
            return data["model"], manager.wifi_firmware

    return f"Wifi version {manager.wifi_firmware}", manager.openevse_firmware


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

    _LOGGER.debug("Checking websocket...")
    manager = hass.data[DOMAIN][config_entry.entry_id][MANAGER]
    if manager.ws_state != "stopped":
        _LOGGER.debug("Closing websocket")
        await manager.ws_disconnect()

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


class OpenEVSEFirmwareCheck(DataUpdateCoordinator):
    """Class to fetch OpenEVSE firmware update data."""

    def __init__(self, hass, interval, config, manager):
        """Initialize."""
        self.interval = timedelta(seconds=interval)
        self.name = f"OpenEVSE ({config.data.get(CONF_NAME)}).firmware"
        self.config = config
        self.hass = hass
        self._manager = manager
        self._data = {}

        _LOGGER.debug("Firmware data will be update every %s", self.interval)

        super().__init__(hass, _LOGGER, name=self.name, update_interval=self.interval)

    async def _async_update_data(self):
        """Return data."""
        self._data = await self._manager.firmware_check()
        _LOGGER.debug("FW Update: %s", self._data)
        return self._data


class OpenEVSEUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching OpenEVSE data."""

    def __init__(self, hass, interval, config, manager):
        """Initialize."""
        self.interval = timedelta(seconds=interval)
        self.name = f"OpenEVSE ({config.data.get(CONF_NAME)})"
        self.config = config
        self.hass = hass
        self._manager = manager
        self._data = {}
        self._manager.callback = self.websocket_update

        _LOGGER.debug("Data will be update every %s", self.interval)

        super().__init__(hass, _LOGGER, name=self.name, update_interval=self.interval)

    async def _async_update_data(self):
        """Return data."""
        await self.update_sensors()
        return self._data

    async def update_sensors(self) -> dict:
        """Update sensor data."""
        try:
            await self._manager.update()
        except RuntimeError:
            pass
        except Exception as error:
            _LOGGER.debug(
                "Error updating sensors [%s]: %s", type(error).__name__, error
            )
            raise UpdateFailed(error) from error

        self.parse_sensors()
        return self._data

    @callback
    def websocket_update(self):
        """Trigger processing updated websocket data."""
        _LOGGER.debug("Websocket update!")
        self.parse_sensors()
        coordinator = self.hass.data[DOMAIN][self.config.entry_id][COORDINATOR]
        coordinator.async_set_updated_data(self._data)

    def parse_sensors(self) -> None:
        """Parse updated sensor data."""
        data = {}
        for sensor in SENSOR_TYPES:  # pylint: disable=consider-using-dict-items
            _sensor = {}
            try:
                sensor_property = SENSOR_TYPES[sensor].key
                _sensor[sensor] = getattr(self._manager, sensor_property)
                _LOGGER.debug(
                    "sensor: %s sensor_property: %s value: %s",
                    sensor,
                    sensor_property,
                    _sensor[sensor],
                )
            except (ValueError, KeyError):
                _LOGGER.info("Could not update status for %s", sensor)
            data.update(_sensor)

        for (
            binary_sensor
        ) in BINARY_SENSORS:  # pylint: disable=consider-using-dict-items
            _sensor = {}
            try:
                sensor_property = BINARY_SENSORS[binary_sensor].key
                # Data can be sent as boolean or as 1/0
                _sensor[binary_sensor] = bool(getattr(self._manager, sensor_property))
                _LOGGER.debug(
                    "binary sensor: %s sensor_property: %s value %s",
                    binary_sensor,
                    sensor_property,
                    _sensor[binary_sensor],
                )
            except (ValueError, KeyError):
                _LOGGER.info(
                    "Could not update status for %s",
                    binary_sensor,
                )
            data.update(_sensor)
        for select in SELECT_TYPES:  # pylint: disable=consider-using-dict-items
            _sensor = {}
            try:
                sensor_property = SELECT_TYPES[select].key
                # Data can be sent as boolean or as 1/0
                _sensor[select] = getattr(self._manager, sensor_property)
                _LOGGER.debug(
                    "select: %s sensor_property: %s value %s",
                    select,
                    sensor_property,
                    _sensor[select],
                )
            except (ValueError, KeyError):
                _LOGGER.info(
                    "Could not update status for %s",
                    select,
                )
            data.update(_sensor)
        _LOGGER.debug("DEBUG: %s", data)
        self._data = data

    async def get_sensors(self) -> dict:
        """Trigger sensor data update."""
        try:
            await self._manager.update()
        except RuntimeError:
            pass
        except Exception as error:
            _LOGGER.error(
                "Error updating sesnors [%s]: %s", type(error).__name__, error
            )

        self.parse_sensors()


async def send_command(handler, command) -> None:
    """Send command to OpenEVSE device via RAPI."""
    cmd, response = await handler.send_command(command)
    _LOGGER.debug("send_command: %s, %s", cmd, response)
    if cmd == command:
        if response == "$NK^21":
            raise InvalidValue
        return None

    raise CommandFailed


class OpenEVSEManager:
    """OpenEVSE connection manager."""

    def __init__(  # pylint: disable-next=unused-argument
        self, hass: HomeAssistant, config_entry: ConfigEntry
    ) -> None:
        """Initialize."""
        self._host = config_entry.data.get(CONF_HOST)
        self._username = config_entry.data.get(CONF_USERNAME)
        self._password = config_entry.data.get(CONF_PASSWORD)
        self.charger = OpenEVSE(self._host, user=self._username, pwd=self._password)


class InvalidValue(Exception):
    """Exception for invalid value errors."""


class CommandFailed(Exception):
    """Exception for invalid command errors."""
