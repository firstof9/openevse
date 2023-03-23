"""OpenEVSE services."""

import logging

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from .const import (
    ATTR_AUTO_RELEASE,
    ATTR_CHARGE_CURRENT,
    ATTR_DEVICE_ID,
    ATTR_ENERGY_LIMIT,
    ATTR_MAX_CURRENT,
    ATTR_STATE,
    ATTR_TIME_LIMIT,
    DOMAIN,
    MANAGER,
    SERVICE_CLEAR_OVERRIDE,
    SERVICE_SET_OVERRIDE,
)

_LOGGER = logging.getLogger(__name__)


class OpenEVSEServices:
    """Class that holds our services."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: ConfigEntry,
    ) -> None:
        """Initialize with hass object."""
        self.hass = hass
        self._config = config

    @callback
    def async_register(self) -> None:
        """Register all our services."""
        self.hass.services.async_register(
            DOMAIN,
            SERVICE_SET_OVERRIDE,
            self._set_override,
            schema=vol.Schema(
                {
                    vol.Required(ATTR_DEVICE_ID): vol.Coerce(str),
                    vol.Optional(ATTR_STATE): vol.Coerce(str),
                    vol.Optional(ATTR_CHARGE_CURRENT): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=48)
                    ),
                    vol.Optional(ATTR_MAX_CURRENT): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=48)
                    ),
                    vol.Optional(ATTR_ENERGY_LIMIT): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=2147483647)
                    ),
                    vol.Optional(ATTR_TIME_LIMIT): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=2147483647)
                    ),
                    vol.Optional(ATTR_AUTO_RELEASE): vol.Coerce(bool),
                }
            ),
        )

        self.hass.services.async_register(
            DOMAIN,
            SERVICE_CLEAR_OVERRIDE,
            self._clear_override,
            schema=vol.Schema(
                {
                    vol.Required(ATTR_DEVICE_ID): vol.Coerce(str),
                }
            ),
        )

    # Setup services
    async def _set_override(self, service: ServiceCall) -> None:
        """Set the override."""
        data = service.data
        if ATTR_DEVICE_ID in data:
            device_id = data[ATTR_DEVICE_ID]
            _LOGGER.debug("Device ID: %s", device_id)
        else:
            raise ValueError

        dev_reg = dr.async_get(self.hass)
        _LOGGER.debug("DR: %s", dir(dev_reg))
        device_entry = dev_reg.async_get(device_id)
        _LOGGER.debug("Device_entry: %s", device_entry)

        if not device_entry:
            raise ValueError(f"Device ID {device_id} is not valid")

        config_id = device_entry.config_entries
        _LOGGER.debug("Config ID: %s", config_id)
        _LOGGER.debug("DEBUG: %s", self.hass.data[DOMAIN][config_id][MANAGER])
        manager = self.hass.data[DOMAIN][config_id][MANAGER]
        _LOGGER.debug("Manager: %s", self._manager)

        if ATTR_STATE in data:
            state = data[ATTR_STATE]
        else:
            state = None
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

    async def _clear_override(self, service: ServiceCall) -> None:
        """Clear the manual override."""
        data = service.data
        if ATTR_DEVICE_ID in data:
            device_id = data[ATTR_DEVICE_ID]
            _LOGGER.debug("Device ID: %s", device_id)
        else:
            raise ValueError
        
        dev_reg = dr.async_get(self.hass)
        device_entry = dev_reg.async_get(device_id)
        _LOGGER.debug("DR: %s", dir(dev_reg))
        _LOGGER.debug("Device_entry: %s", device_entry)

        if not device_entry:
            raise ValueError(f"Device ID {device_id} is not valid")

        config_id = device_entry.config_entries   
        manager = self.hass.data[DOMAIN][config_id][MANAGER]

        await manager.clear_override()
        _LOGGER.debug("Override clear command sent.")
