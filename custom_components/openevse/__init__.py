"""The openevse component."""

from __future__ import annotations

import asyncio
import functools
import inspect
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    EVENT_HOMEASSISTANT_STARTED,
)
from homeassistant.core import (
    CoreState,
    Event,
    EventStateChangedData,
    HomeAssistant,
    callback,
)
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from openevsehttp.__main__ import OpenEVSE
from openevsehttp.exceptions import MissingSerial, UnsupportedFeature

from .const import (
    BINARY_SENSORS,
    CONF_GRID,
    CONF_INVERT,
    CONF_NAME,
    CONF_SHAPER,
    CONF_SOLAR,
    CONF_VOLTAGE,
    COORDINATOR,
    DOMAIN,
    FW_COORDINATOR,
    ISSUE_URL,
    LIGHT_TYPES,
    MANAGER,
    NUMBER_TYPES,
    PLATFORMS,
    SELECT_TYPES,
    SENSOR_FIELDS,
    SENSOR_TYPES,
    TIMEOUT_ERROR,
    UNSUB_LISTENERS,
    VERSION,
)
from .services import OpenEVSEServices

_LOGGER = logging.getLogger(__name__)

divert_mode = {
    0: "eco",
    1: "fast",
}


@callback
async def handle_state_change(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    event: Event[EventStateChangedData] | None = None,
) -> None:
    """Track state changes to sensor entities."""
    manager = hass.data[DOMAIN][config_entry.entry_id][MANAGER]
    options = config_entry.options
    invert = options.get(CONF_INVERT)
    grid_sensor = options.get(CONF_GRID)
    solar_sensor = options.get(CONF_SOLAR)
    voltage_sensor = options.get(CONF_VOLTAGE)
    shaper_sensor = options.get(CONF_SHAPER)
    changed_entity = event.data["entity_id"]

    if grid_sensor is not None and changed_entity == grid_sensor:
        state = hass.states.get(grid_sensor)
        grid = state.state if state else None
        if grid in [None, "unavailable", "unknown"]:
            grid = None
        else:
            try:
                grid = round(float(grid))
            except (ValueError, TypeError):
                _LOGGER.warning("Non-numeric state for grid sensor: %s", grid)
                grid = None

        _LOGGER.debug("Sending sensor data to OpenEVSE: (grid: %s)", grid)
        try:
            await manager.self_production(grid=grid, solar=None, invert=invert)
        except TimeoutError as err:
            _LOGGER.exception(TIMEOUT_ERROR, err)

    elif solar_sensor is not None and changed_entity == solar_sensor:
        state = hass.states.get(solar_sensor)
        solar = state.state if state else None
        if solar in [None, "unavailable", "unknown"]:
            solar = None
        else:
            try:
                solar = round(float(solar))
            except (ValueError, TypeError):
                _LOGGER.warning("Non-numeric state for solar sensor: %s", solar)
                solar = None

        _LOGGER.debug("Sending sensor data to OpenEVSE: (solar: %s)", solar)
        try:
            await manager.self_production(grid=None, solar=solar, invert=False)
        except TimeoutError as err:
            _LOGGER.exception(TIMEOUT_ERROR, err)

    if voltage_sensor is not None and changed_entity == voltage_sensor:
        state = hass.states.get(voltage_sensor)
        voltage = state.state if state else None
        if voltage in [None, "unavailable", "unknown"]:
            voltage = None
        else:
            try:
                voltage = round(float(voltage))
            except (ValueError, TypeError):
                _LOGGER.warning("Non-numeric state for voltage sensor: %s", voltage)
                voltage = None

        _LOGGER.debug("Sending sensor data to OpenEVSE: (voltage: %s)", voltage)
        try:
            await manager.grid_voltage(voltage=voltage)
        except TimeoutError as err:
            _LOGGER.exception(TIMEOUT_ERROR, err)

    if shaper_sensor is not None and changed_entity == shaper_sensor:
        state = hass.states.get(shaper_sensor)
        power = state.state if state else None
        if power in [None, "unavailable", "unknown", ""]:
            power = None
        else:
            try:
                power = round(float(power))
            except (ValueError, TypeError):
                _LOGGER.warning("Non-numeric state for shaper sensor: %s", power)
                power = None

        _LOGGER.debug("Sending sensor data to OpenEVSE: (shaper: %s)", power)
        try:
            await manager.set_shaper_live_pwr(power=power)
        except TimeoutError as err:
            _LOGGER.exception(TIMEOUT_ERROR, err)


async def homeassistant_started_listener(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    sensors: list,
    event: Event = None,
):
    """Start tracking state changes after HomeAssistant has started."""
    # Listen to sensor state changes so we can fire an event
    hass.data[DOMAIN][config_entry.entry_id][UNSUB_LISTENERS].append(
        async_track_state_change_event(
            hass,
            sensors,
            functools.partial(handle_state_change, hass, config_entry),
        )
    )


async def async_setup(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
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

    manager = OpenEVSEManager(hass, config_entry).charger
    interval = 60
    coordinator = OpenEVSEUpdateCoordinator(hass, interval, config_entry, manager)
    fw_coordinator = OpenEVSEFirmwareCheck(hass, 86400, config_entry, manager)

    hass.data[DOMAIN][config_entry.entry_id] = {
        COORDINATOR: coordinator,
        MANAGER: manager,
        FW_COORDINATOR: fw_coordinator,
        UNSUB_LISTENERS: [],
    }

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()
    await fw_coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    model_info, sw_version = await get_firmware(manager)

    try:
        data = await manager.test_and_get()
        serial = data["serial"]
    except MissingSerial:
        _LOGGER.info("Unable to find serial number.")
        serial = config_entry.entry_id

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

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    # Only register services if supported by firmware
    if manager.version_check("4.1.0"):
        services = OpenEVSEServices(hass, config_entry)
        services.async_register()

    sensors = []
    options = config_entry.options
    if options.get(CONF_GRID):
        sensors.append(options.get(CONF_GRID))
    if options.get(CONF_SOLAR):
        sensors.append(options.get(CONF_SOLAR))
    if options.get(CONF_VOLTAGE):
        sensors.append(options.get(CONF_VOLTAGE))
    if options.get(CONF_SHAPER):
        sensors.append(options.get(CONF_SHAPER))

    if len(sensors) > 0:
        if hass.state == CoreState.running:
            await homeassistant_started_listener(hass, config_entry, sensors)
        else:
            hass.bus.async_listen_once(
                EVENT_HOMEASSISTANT_STARTED,
                functools.partial(
                    homeassistant_started_listener, hass, config_entry, sensors
                ),
            )

    config_entry.async_on_unload(config_entry.add_update_listener(update_listener))

    return True


async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Handle options update - reload integration."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate config entry from version 1 to version 2."""
    _LOGGER.debug(
        "Migrating config entry from version %s to version 2",
        config_entry.version,
    )

    if config_entry.version == 1:
        new_data = dict(config_entry.data)
        new_options = dict(config_entry.options)

        # Move sensor fields from data to options
        for key in SENSOR_FIELDS:
            if key in new_data:
                new_options[key] = new_data.pop(key)

        hass.config_entries.async_update_entry(
            config_entry, data=new_data, options=new_options, version=2
        )
        _LOGGER.info(
            "Migration to version 2 successful: sensor options moved to options flow"
        )

    return True


async def get_firmware(manager: OpenEVSEManager) -> tuple:
    """Get firmware version."""
    _LOGGER.debug("Getting firmware versions...")
    data = {}
    try:
        await manager.update()
    except Exception as error:
        _LOGGER.exception("Problem retrieving firmware data: %s", error)
        return "", ""

    try:
        data = await manager.test_and_get()
    except MissingSerial:
        _LOGGER.info("Missing serial number data, skipping...")

    if data and data.get("model") and data.get("model") != "unknown":
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
        # Unsubscribe to any listeners
        for unsub_listener in hass.data[DOMAIN][config_entry.entry_id].get(
            UNSUB_LISTENERS, []
        ):
            unsub_listener()
        hass.data[DOMAIN][config_entry.entry_id].get(UNSUB_LISTENERS, []).clear()
        _LOGGER.debug("Successfully removed entities from the %s integration", DOMAIN)
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok


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

        super().__init__(
            hass,
            _LOGGER,
            config_entry=config,
            name=self.name,
            update_interval=self.interval,
        )

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

        super().__init__(
            hass,
            _LOGGER,
            config_entry=config,
            name=self.name,
            update_interval=self.interval,
        )

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

        if self._manager.ws_state != "connected":
            _LOGGER.debug("Connecting to websocket...")
            try:
                self._manager.ws_start()
            except RuntimeError:
                pass
            except Exception as error:
                _LOGGER.debug(
                    "Error connecting to websocket [%s]: %s",
                    type(error).__name__,
                    error,
                )
                raise UpdateFailed(error) from error

        try:
            new_data = self.parse_sensors()
            new_data.update(await self.async_parse_sensors())
            self._data = new_data
        except Exception as error:
            _LOGGER.debug("Error parsing sensors [%s]: %s", type(error).__name__, error)
            raise UpdateFailed(error) from error

        _LOGGER.debug("Coordinator data: %s", self._data)
        return self._data

    @callback
    async def websocket_update(self):
        """Trigger processing updated websocket data."""
        _LOGGER.debug("Websocket update!")
        try:
            new_data = self.parse_sensors()
            new_data.update(await self.async_parse_sensors())
            self._data = new_data
        except (ValueError, KeyError, UnsupportedFeature) as error:
            _LOGGER.debug("Error parsing sensors [%s]: %s", type(error).__name__, error)
            return
        except Exception as error:
            _LOGGER.warning(
                "Unexpected error parsing sensors [%s]: %s",
                type(error).__name__,
                error,
                exc_info=True,
            )
            return
        try:
            coordinator = self.hass.data[DOMAIN][self.config.entry_id][COORDINATOR]
            coordinator.async_set_updated_data(self._data)
        except KeyError as err:
            _LOGGER.error("Error locating configuration: %s", err)

    def _collect_values(
        self, descriptors, label, value_cast=None, skip_async=True
    ) -> dict:
        """Collect values from descriptors."""
        data = {}
        manager_dir = dir(self._manager)
        for key, descriptor in descriptors.items():
            if skip_async and getattr(descriptor, "is_async_value", False):
                continue
            sensor_property = descriptor.key
            if sensor_property not in manager_dir:
                _LOGGER.debug("Could not update status for %s", key)
                continue

            try:
                value = getattr(self._manager, sensor_property)
                if value_cast:
                    value = value_cast(value)
                _LOGGER.debug(
                    "%s: %s sensor_property: %s value: %s",
                    label,
                    key,
                    sensor_property,
                    value,
                )
                data[key] = value
            except (ValueError, KeyError, UnsupportedFeature):
                _LOGGER.debug("Could not update status for %s", key)
                continue
        return data

    async def _collect_async_values(self, descriptors, label) -> dict:
        """Collect async values from descriptors."""
        data = {}
        seen_results = {}
        manager_dir = dir(self._manager)
        for key, descriptor in descriptors.items():
            if not getattr(descriptor, "is_async_value", False):
                continue
            sensor_property = descriptor.key
            sensor_value = getattr(descriptor, "value", None)
            if sensor_value not in manager_dir:
                _LOGGER.debug("Could not update status for %s", key)
                continue

            if sensor_value in seen_results:
                data[key] = seen_results[sensor_value]
                _LOGGER.debug(
                    "%s: %s sensor_property: %s value %s",
                    label,
                    key,
                    sensor_property,
                    data[key],
                )
                continue

            try:
                attr = getattr(self._manager, sensor_value)
                result = attr() if callable(attr) else attr

                if inspect.isawaitable(result):
                    val = await result
                else:
                    val = result

                seen_results[sensor_value] = val
                data[key] = val
                _LOGGER.debug(
                    "%s: %s sensor_property: %s value %s",
                    label,
                    key,
                    sensor_property,
                    data[key],
                )
            except (ValueError, KeyError, UnsupportedFeature):
                _LOGGER.debug("Could not update status for %s", key)
                continue
        return data

    def parse_sensors(self) -> dict:
        """Parse updated sensor data."""
        data = {}
        data.update(self._collect_values(SENSOR_TYPES, "sensor"))
        data.update(self._collect_values(BINARY_SENSORS, "binary sensor", bool))
        data.update(self._collect_values(SELECT_TYPES, "select"))
        data.update(self._collect_values(NUMBER_TYPES, "number"))
        data.update(self._collect_values(LIGHT_TYPES, "light"))
        _LOGGER.debug("Parsed data: %s", data)
        return data

    async def async_parse_sensors(self) -> dict:
        """Parse updated sensor data using async."""
        data = {}
        data.update(await self._collect_async_values(SELECT_TYPES, "select"))
        data.update(await self._collect_async_values(NUMBER_TYPES, "number"))
        data.update(await self._collect_async_values(SENSOR_TYPES, "sensor"))
        _LOGGER.debug("Parsed async data: %s", data)
        return data


async def send_command(handler, command) -> None:
    """Send command to OpenEVSE device via RAPI."""
    cmd, response = await handler.send_command(command)
    _LOGGER.debug("send_command: %s, %s", cmd, response)
    if cmd == command:
        if response == "$NK^21":
            raise InvalidValueError
        return None

    raise CommandFailedError


class OpenEVSEManager:
    """OpenEVSE connection manager."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize."""
        self._host = config_entry.data.get(CONF_HOST)
        self._username = config_entry.data.get(CONF_USERNAME)
        self._password = config_entry.data.get(CONF_PASSWORD)
        self.charger = OpenEVSE(self._host, user=self._username, pwd=self._password)


class InvalidValueError(Exception):
    """Exception for invalid value errors."""


class CommandFailedError(Exception):
    """Exception for invalid command errors."""
