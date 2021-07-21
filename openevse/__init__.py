"""The openevse component."""
from .const import (
    CONF_NAME,
    SENSOR_TYPES,
    VERSION,
    ISSUE_URL,
    DOMAIN,
    COORDINATOR,
    PLATFORMS,
)
from datetime import timedelta
import logging
import openevsewifi
from requests import RequestException
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_USERNAME,
    CONF_PASSWORD,
)
from homeassistant.core import Config, HomeAssistant

_LOGGER = logging.getLogger(__name__)


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

    interval = 1
    coordinator = OpenEVSEUpdateCoordinator(hass, interval, config_entry)

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    hass.data[DOMAIN][config_entry.entry_id] = {
        COORDINATOR: coordinator,
    }

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, platform)
        )

    return True


def get_sensors(hass, config) -> dict:

    data = {}
    host = config.data.get(CONF_HOST)
    username = config.data.get(CONF_USERNAME)
    password = config.data.get(CONF_PASSWORD)
    charger = openevsewifi.Charger(host, username=username, password=password)

    for sensor in SENSOR_TYPES:
        _sensor = {}
        try:
            sensor_name = SENSOR_TYPES[sensor]
            sensor_property = SENSOR_TYPES[sensor][2]
            _sensor[sensor_name] = getattr(charger, sensor_property)
        except (RequestException, ValueError, KeyError):
            _LOGGER.warning("Could not update status for %s", sensor_name)
        data.update(_sensor)
    _LOGGER.warning("DEBUG: %s", data)
    return data


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
