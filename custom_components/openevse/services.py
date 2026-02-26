"""OpenEVSE services."""

import logging

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
    callback,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr

from .const import (
    ATTR_AUTO_RELEASE,
    ATTR_CHARGE_CURRENT,
    ATTR_DEVICE_ID,
    ATTR_ENERGY_LIMIT,
    ATTR_MAX_CURRENT,
    ATTR_STATE,
    ATTR_TIME_LIMIT,
    ATTR_TYPE,
    ATTR_VALUE,
    DOMAIN,
    MANAGER,
    SERVICE_CLEAR_LIMIT,
    SERVICE_CLEAR_OVERRIDE,
    SERVICE_GET_LIMIT,
    SERVICE_LIST_CLAIMS,
    SERVICE_LIST_OVERRIDES,
    SERVICE_MAKE_CLAIM,
    SERVICE_RELEASE_CLAIM,
    SERVICE_SET_LIMIT,
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
                    vol.Required(ATTR_DEVICE_ID): vol.All(cv.ensure_list, [cv.string]),
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
            SERVICE_SET_LIMIT,
            self._set_limit,
            schema=vol.Schema(
                {
                    vol.Required(ATTR_DEVICE_ID): vol.All(cv.ensure_list, [cv.string]),
                    vol.Required(ATTR_TYPE): vol.Coerce(str),
                    vol.Required(ATTR_VALUE): vol.Coerce(int),
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
                    vol.Required(ATTR_DEVICE_ID): vol.All(cv.ensure_list, [cv.string]),
                }
            ),
        )

        self.hass.services.async_register(
            DOMAIN,
            SERVICE_CLEAR_LIMIT,
            self._clear_limit,
            schema=vol.Schema(
                {
                    vol.Required(ATTR_DEVICE_ID): vol.All(cv.ensure_list, [cv.string]),
                }
            ),
        )

        self.hass.services.async_register(
            DOMAIN,
            SERVICE_GET_LIMIT,
            self._get_limit,
            schema=vol.Schema(
                {
                    vol.Required(ATTR_DEVICE_ID): vol.All(cv.ensure_list, [cv.string]),
                }
            ),
            supports_response=SupportsResponse.ONLY,
        )

        self.hass.services.async_register(
            DOMAIN,
            SERVICE_MAKE_CLAIM,
            self._make_claim,
            schema=vol.Schema(
                {
                    vol.Required(ATTR_DEVICE_ID): vol.All(cv.ensure_list, [cv.string]),
                    vol.Optional(ATTR_STATE): vol.Coerce(str),
                    vol.Optional(ATTR_CHARGE_CURRENT): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=48)
                    ),
                    vol.Optional(ATTR_MAX_CURRENT): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=48)
                    ),
                    vol.Optional(ATTR_AUTO_RELEASE): vol.Coerce(bool),
                }
            ),
        )

        self.hass.services.async_register(
            DOMAIN,
            SERVICE_LIST_CLAIMS,
            self._list_claims,
            schema=vol.Schema(
                {
                    vol.Required(ATTR_DEVICE_ID): vol.All(cv.ensure_list, [cv.string]),
                }
            ),
            supports_response=SupportsResponse.ONLY,
        )

        self.hass.services.async_register(
            DOMAIN,
            SERVICE_RELEASE_CLAIM,
            self._release_claim,
            schema=vol.Schema(
                {
                    vol.Required(ATTR_DEVICE_ID): vol.All(cv.ensure_list, [cv.string]),
                }
            ),
        )

        self.hass.services.async_register(
            DOMAIN,
            SERVICE_LIST_OVERRIDES,
            self._list_overrides,
            schema=vol.Schema(
                {
                    vol.Required(ATTR_DEVICE_ID): vol.All(cv.ensure_list, [cv.string]),
                }
            ),
            supports_response=SupportsResponse.ONLY,
        )

    # Setup services
    async def _set_override(self, service: ServiceCall) -> None:
        """Set the override."""
        data = service.data
        for device in data[ATTR_DEVICE_ID]:
            device_id = device
            _LOGGER.debug("Device ID: %s", device_id)

            dev_reg = dr.async_get(self.hass)
            device_entry = dev_reg.async_get(device_id)
            _LOGGER.debug("Device_entry: %s", device_entry)

            if not device_entry:
                raise ValueError(f"Device ID {device_id} is not valid")

            if not device_entry.connections:
                raise ValueError(f"Device ID {device_id} has no connections")

            config_id = next(iter(device_entry.connections))[1]
            _LOGGER.debug("Config ID: %s", config_id)
            try:
                manager = self.hass.data[DOMAIN][config_id][MANAGER]
                state = data.get(ATTR_STATE)
                charge_current = data.get(ATTR_CHARGE_CURRENT)
                max_current = data.get(ATTR_MAX_CURRENT)
                energy_limit = data.get(ATTR_ENERGY_LIMIT)
                time_limit = data.get(ATTR_TIME_LIMIT)
                auto_release = data.get(ATTR_AUTO_RELEASE)

                response = await manager.set_override(
                    state=state,
                    charge_current=charge_current,
                    max_current=max_current,
                    energy_limit=energy_limit,
                    time_limit=time_limit,
                    auto_release=auto_release,
                )
                _LOGGER.debug("Set Override response: %s", response)

            except KeyError as err:
                _LOGGER.error("Error locating configuration: %s", err)

    async def _clear_override(self, service: ServiceCall) -> None:
        """Clear the manual override."""
        data = service.data
        _LOGGER.debug("Data: %s", data)
        for device in data[ATTR_DEVICE_ID]:
            device_id = device
            _LOGGER.debug("Device ID: %s", device_id)

            dev_reg = dr.async_get(self.hass)
            device_entry = dev_reg.async_get(device_id)
            _LOGGER.debug("Device_entry: %s", device_entry)

            if not device_entry:
                raise ValueError(f"Device ID {device_id} is not valid")

            if not device_entry.connections:
                raise ValueError(f"Device ID {device_id} has no connections")

            config_id = next(iter(device_entry.connections))[1]
            _LOGGER.debug("Config ID: %s Type: %s", config_id, type(config_id))
            try:
                manager = self.hass.data[DOMAIN][config_id][MANAGER]
                await manager.clear_override()
                _LOGGER.debug("Override clear command sent.")
            except KeyError as err:
                _LOGGER.error("Error locating configuration: %s", err)

    async def _set_limit(self, service: ServiceCall) -> None:
        """Set the limit."""
        data = service.data
        for device in data[ATTR_DEVICE_ID]:
            device_id = device
            _LOGGER.debug("Device ID: %s", device_id)

            dev_reg = dr.async_get(self.hass)
            device_entry = dev_reg.async_get(device_id)
            _LOGGER.debug("Device_entry: %s", device_entry)

            if not device_entry:
                raise ValueError(f"Device ID {device_id} is not valid")

            if not device_entry.connections:
                raise ValueError(f"Device ID {device_id} has no connections")

            config_id = next(iter(device_entry.connections))[1]
            _LOGGER.debug("Config ID: %s", config_id)
            try:
                manager = self.hass.data[DOMAIN][config_id][MANAGER]
                limit_type = data[ATTR_TYPE]
                value = data[ATTR_VALUE]

                if ATTR_AUTO_RELEASE in data:
                    auto_release = data[ATTR_AUTO_RELEASE]
                else:
                    auto_release = None

                response = await manager.set_limit(
                    limit_type=limit_type,
                    value=value,
                    release=auto_release,
                )
                _LOGGER.debug("Set Limit response: %s", response)

            except KeyError as err:
                _LOGGER.error("Error locating configuration: %s", err)

    async def _clear_limit(self, service: ServiceCall) -> None:
        """Clear the limit."""
        data = service.data
        _LOGGER.debug("Data: %s", data)
        for device in data[ATTR_DEVICE_ID]:
            device_id = device
            _LOGGER.debug("Device ID: %s", device_id)

            dev_reg = dr.async_get(self.hass)
            device_entry = dev_reg.async_get(device_id)
            _LOGGER.debug("Device_entry: %s", device_entry)

            if not device_entry:
                raise ValueError(f"Device ID {device_id} is not valid")

            if not device_entry.connections:
                raise ValueError(f"Device ID {device_id} has no connections")

            config_id = next(iter(device_entry.connections))[1]
            _LOGGER.debug("Config ID: %s Type: %s", config_id, type(config_id))
            try:
                manager = self.hass.data[DOMAIN][config_id][MANAGER]
                await manager.clear_limit()
                _LOGGER.debug("Limit clear command sent.")
            except KeyError as err:
                _LOGGER.error("Error locating configuration: %s", err)

    async def _get_limit(self, service: ServiceCall) -> ServiceResponse:
        """Get the limit."""
        data = service.data
        _LOGGER.debug("Data: %s", data)
        for device in data[ATTR_DEVICE_ID]:
            device_id = device
            _LOGGER.debug("Device ID: %s", device_id)

            dev_reg = dr.async_get(self.hass)
            device_entry = dev_reg.async_get(device_id)
            _LOGGER.debug("Device_entry: %s", device_entry)

            if not device_entry:
                raise ValueError(f"Device ID {device_id} is not valid")

            if not device_entry.connections:
                raise ValueError(f"Device ID {device_id} has no connections")

            config_id = next(iter(device_entry.connections))[1]
            _LOGGER.debug("Config ID: %s Type: %s", config_id, type(config_id))
            try:
                manager = self.hass.data[DOMAIN][config_id][MANAGER]
                response = await manager.get_limit()
                _LOGGER.debug("Get limit response %s.", response)
                return response
            except KeyError as err:
                _LOGGER.error("Error locating configuration: %s", err)
                return {}

    async def _make_claim(self, service: ServiceCall) -> None:
        """Make a claim."""
        data = service.data
        for device in data[ATTR_DEVICE_ID]:
            device_id = device
            _LOGGER.debug("Device ID: %s", device_id)

            dev_reg = dr.async_get(self.hass)
            device_entry = dev_reg.async_get(device_id)
            _LOGGER.debug("Device_entry: %s", device_entry)

            if not device_entry:
                raise ValueError(f"Device ID {device_id} is not valid")

            if not device_entry.connections:
                raise ValueError(f"Device ID {device_id} has no connections")

            config_id = next(iter(device_entry.connections))[1]
            _LOGGER.debug("Config ID: %s", config_id)
            try:
                manager = self.hass.data[DOMAIN][config_id][MANAGER]
                state = data.get(ATTR_STATE)
                charge_current = data.get(ATTR_CHARGE_CURRENT)
                max_current = data.get(ATTR_MAX_CURRENT)
                auto_release = data.get(ATTR_AUTO_RELEASE)

                response = await manager.make_claim(
                    state=state,
                    charge_current=charge_current,
                    max_current=max_current,
                    auto_release=auto_release,
                )
                _LOGGER.debug("Make claim response: %s", response)
            except KeyError as err:
                _LOGGER.error("Error locating configuration: %s", err)

    async def _release_claim(self, service: ServiceCall) -> None:
        """Release a claim."""
        data = service.data
        _LOGGER.debug("Data: %s", data)
        for device in data[ATTR_DEVICE_ID]:
            device_id = device
            _LOGGER.debug("Device ID: %s", device_id)

            dev_reg = dr.async_get(self.hass)
            device_entry = dev_reg.async_get(device_id)
            _LOGGER.debug("Device_entry: %s", device_entry)

            if not device_entry:
                raise ValueError(f"Device ID {device_id} is not valid")

            if not device_entry.connections:
                raise ValueError(f"Device ID {device_id} has no connections")

            config_id = next(iter(device_entry.connections))[1]
            _LOGGER.debug("Config ID: %s Type: %s", config_id, type(config_id))
            try:
                manager = self.hass.data[DOMAIN][config_id][MANAGER]
                await manager.release_claim()
                _LOGGER.debug("Release claim command sent.")
            except KeyError as err:
                _LOGGER.error("Error locating configuration: %s", err)

    async def _list_claims(self, service: ServiceCall) -> ServiceResponse:
        """Get the claims."""
        data = service.data
        _LOGGER.debug("Data: %s", data)
        for device in data[ATTR_DEVICE_ID]:
            device_id = device
            _LOGGER.debug("Device ID: %s", device_id)

            dev_reg = dr.async_get(self.hass)
            device_entry = dev_reg.async_get(device_id)
            _LOGGER.debug("Device_entry: %s", device_entry)

            if not device_entry:
                raise ValueError(f"Device ID {device_id} is not valid")

            if not device_entry.connections:
                raise ValueError(f"Device ID {device_id} has no connections")

            config_id = next(iter(device_entry.connections))[1]
            _LOGGER.debug("Config ID: %s Type: %s", config_id, type(config_id))
            try:
                manager = self.hass.data[DOMAIN][config_id][MANAGER]
                response = await manager.list_claims()
                _LOGGER.debug("List claims response %s.", response)
                claims = {}
                for x, claim in enumerate(response):
                    claims[x] = claim
                _LOGGER.debug("Processed response %s.", claims)
                return claims
            except KeyError as err:
                _LOGGER.error("Error locating configuration: %s", err)
                return {}

    async def _list_overrides(self, service: ServiceCall) -> ServiceResponse:
        """Get the overrides."""
        data = service.data
        _LOGGER.debug("Data: %s", data)
        for device in data[ATTR_DEVICE_ID]:
            device_id = device
            _LOGGER.debug("Device ID: %s", device_id)

            dev_reg = dr.async_get(self.hass)
            device_entry = dev_reg.async_get(device_id)
            _LOGGER.debug("Device_entry: %s", device_entry)

            if not device_entry:
                raise ValueError(f"Device ID {device_id} is not valid")

            config_id = next(iter(device_entry.connections))[1]
            _LOGGER.debug("Config ID: %s Type: %s", config_id, type(config_id))
            try:
                manager = self.hass.data[DOMAIN][config_id][MANAGER]
                response = await manager.get_override()
                _LOGGER.debug("List overrides response %s.", response)
                return response
            except KeyError as err:
                _LOGGER.error("Error locating configuration: %s", err)
                return {}
