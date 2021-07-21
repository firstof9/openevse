"""Adds config flow for OpenEVSE."""
import logging
from typing import Any, Dict, Optional, Union

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.util import slugify

from .const import CONF_NAME, DEFAULT_HOST, DEFAULT_NAME, DOMAIN


@config_entries.HANDLERS.register(DOMAIN)
class OpenEVSEFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for KeyMaster."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL
    DEFAULTS = {CONF_HOST: DEFAULT_HOST, CONF_NAME: DEFAULT_NAME}

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


def _get_schema(
    hass: HomeAssistant,
    user_input: Optional[Dict[str, Any]],
    default_dict: Dict[str, Any],
    entry_id: str = None,
) -> vol.Schema:
    """Gets a schema using the default_dict as a backup."""
    if user_input is None:
        user_input = {}

    def _get_default(key: str, fallback_default: Any = None) -> None:
        """Gets default value for key."""
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

        # TODO: Insert openevse connection check here

        # Update options if no errors
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
