"""Adds config flow for OpenEVSE."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Union

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components import zeroconf
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import AbortFlow, FlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.util import slugify
from openevsehttp.__main__ import OpenEVSE

from .const import (
    CONF_GRID,
    CONF_INVERT,
    CONF_NAME,
    CONF_SERIAL,
    CONF_SOLAR,
    CONF_VOLTAGE,
    DEFAULT_HOST,
    DEFAULT_NAME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class OpenEVSEFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for KeyMaster."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL
    DEFAULTS = {CONF_HOST: DEFAULT_HOST, CONF_NAME: DEFAULT_NAME}

    def __init__(self):
        """Set up the instance."""
        self.discovery_info = {}

    async def async_step_discovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm discovery."""
        _LOGGER.debug("config_flow async_step_discovery_confirm")
        if user_input is None:
            return self.async_show_form(
                step_id="discovery_confirm",
                description_placeholders={"name": self.discovery_info[CONF_NAME]},
                errors={},
            )

        return self.async_create_entry(
            title=self.discovery_info[CONF_NAME],
            data=self.discovery_info,
        )

    @staticmethod
    async def _async_try_connect_and_fetch(ip_address: str) -> dict[str, Any]:
        """Try to connect."""
        _LOGGER.debug("config_flow _async_try_connect_and_fetch")

        # Make connection with device
        # This is to test the connection and to get info for unique_id
        charger = OpenEVSE(ip_address)

        try:
            await charger.update()

        except Exception as ex:
            _LOGGER.exception(
                "Error connecting with OpenEVSE at %s",
                ip_address,
            )
            raise AbortFlow("unknown_error") from ex

        await charger.ws_disconnect()

    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> FlowResult:
        """Handle zeroconf discovery."""
        _LOGGER.debug("config_flow async_step_zeroconf")

        # Avoid probing devices that already have an entry
        self._async_abort_entries_match({CONF_HOST: discovery_info.host})

        # Validate discovery entry
        if CONF_SERIAL not in discovery_info.properties:
            return self.async_abort(reason="invalid_discovery_parameters")

        host = discovery_info.host
        serial = discovery_info.properties[CONF_SERIAL]
        # model = discovery_info.properties[CONF_TYPE]
        name = f"OpenEVSE: {discovery_info.name.split('.')[0]}"

        self.discovery_info.update(
            {
                CONF_HOST: host,
                CONF_NAME: name,
            }
        )

        self.context.update({"title_placeholders": {"name": name}})

        # Test connection to device
        await self._async_try_connect_and_fetch(host)

        unique_id = f"{name}_{serial}"

        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured(
            updates={
                CONF_HOST: host,
                CONF_NAME: name,
            },
        )

        return await self.async_step_discovery_confirm()

    async def async_step_user(
        self, user_input: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Handle a flow initialized by the user."""
        return await _start_config_flow(
            self,
            "user",
            user_input[CONF_NAME] if user_input else None,
            user_input,
            self.DEFAULTS,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Handle options flow."""
        return OpenEVSEOptionsFlow(config_entry)


class OpenEVSEOptionsFlow(config_entries.OptionsFlow):
    """Options flow for KeyMaster."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Handle a flow initialized by the user."""
        return await _start_config_flow(
            self,
            "init",
            "",
            user_input,
            self.config_entry.data,
            self.config_entry.entry_id,
        )


def _get_schema(  # pylint: disable-next=unused-argument
    hass: HomeAssistant,
    user_input: Optional[Dict[str, Any]],
    default_dict: Dict[str, Any],
    # pylint: disable-next=unused-argument
    entry_id: str = None,
) -> vol.Schema:
    """Get a schema using the default_dict as a backup."""
    if user_input is None:
        user_input = {}

    def _get_default(key: str, fallback_default: Any = None) -> None:
        """Get default value for key."""
        return user_input.get(key, default_dict.get(key, fallback_default))

    return vol.Schema(
        {
            vol.Optional(
                CONF_NAME, default=_get_default(CONF_NAME, DEFAULT_NAME)
            ): cv.string,
            vol.Required(
                CONF_HOST, default=_get_default(CONF_HOST, DEFAULT_HOST)
            ): cv.string,
            vol.Optional(
                CONF_USERNAME, default=_get_default(CONF_USERNAME, "")
            ): cv.string,
            vol.Optional(
                CONF_PASSWORD, default=_get_default(CONF_PASSWORD, "")
            ): cv.string,
            vol.Optional(CONF_GRID, default=_get_default(CONF_GRID, "")): cv.string,
            vol.Optional(CONF_SOLAR, default=_get_default(CONF_SOLAR, "")): cv.string,
            vol.Optional(
                CONF_VOLTAGE, default=_get_default(CONF_VOLTAGE, "")
            ): cv.string,
            vol.Optional(CONF_INVERT, default=_get_default(CONF_INVERT, False)): bool,
        },
    )


def _show_config_form(
    cls: Union[OpenEVSEFlowHandler, OpenEVSEOptionsFlow],
    step_id: str,
    user_input: Dict[str, Any],
    errors: Dict[str, str],
    description_placeholders: Dict[str, str],
    defaults: Dict[str, Any] = None,
    entry_id: str = None,
) -> Dict[str, Any]:
    """Show the configuration form to edit location data."""
    return cls.async_show_form(
        step_id=step_id,
        data_schema=_get_schema(cls.hass, user_input, defaults, entry_id),
        errors=errors,
        description_placeholders=description_placeholders,
    )


async def _start_config_flow(
    cls: Union[OpenEVSEFlowHandler, OpenEVSEOptionsFlow],
    step_id: str,
    title: str,
    user_input: Dict[str, Any],
    defaults: Dict[str, Any] = None,
    entry_id: str = None,
):
    """Start a config flow."""
    errors = {}
    description_placeholders = {}

    if user_input is not None:
        user_input[CONF_NAME] = slugify(user_input[CONF_NAME].lower())

        charger = OpenEVSE(
            user_input[CONF_HOST],
            user=user_input[CONF_USERNAME],
            pwd=user_input[CONF_PASSWORD],
        )

        try:
            await charger.update()
            await charger.ws_disconnect()
        except Exception as ex:
            _LOGGER.exception(
                "Error connecting with OpenEVSE at %s: %s",
                user_input[CONF_HOST],
                ex,
            )
            errors[CONF_HOST] = "communication"

        if not errors:
            return cls.async_create_entry(title=title, data=user_input)

        return _show_config_form(
            cls,
            step_id,
            user_input,
            errors,
            description_placeholders,
            defaults,
            entry_id,
        )

    return _show_config_form(
        cls,
        step_id,
        user_input,
        errors,
        description_placeholders,
        defaults,
        entry_id,
    )
