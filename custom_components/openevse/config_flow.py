"""Adds config flow for OpenEVSE."""
from __future__ import annotations
import logging
from typing import Any, Dict, Optional, Union

import voluptuous as vol
from homeassistant.config_entries import (
    SOURCE_ZEROCONF,
    ConfigEntry,
    ConfigFlow,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import DiscoveryInfoType
from homeassistant.util import slugify

from .const import CONF_NAME, CONF_ID, DEFAULT_HOST, DEFAULT_NAME, DOMAIN


class OpenEVSEFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for KeyMaster."""

    VERSION = 1
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

    async def async_step_zeroconf(
        self, discovery_info: DiscoveryInfoType
    ) -> FlowResult:
        """Handle zeroconf discovery."""

        # Hostname is format: wled-livingroom.local.
        host = discovery_info["hostname"].rstrip(".")
        name, _ = host.rsplit(".")

        self.context.update(
            {
                CONF_HOST: discovery_info["hostname"],
                CONF_NAME: name,
                CONF_ID: discovery_info["properties"].get(CONF_ID),
                "title_placeholders": {"name": name},
            }
        )

        # Prepare configuration flow
        return await _start_config_flow(
            self,
            SOURCE_ZEROCONF,
            self.context.get(CONF_NAME),
            discovery_info,
            None,
            True,
        )

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by zeroconf."""
        return await _start_config_flow(
            self, SOURCE_ZEROCONF, user_input[CONF_NAME], user_input
        )

    def _show_confirm_dialog(self, errors: dict | None = None) -> FlowResult:
        """Show the confirm dialog to the user."""
        name = self.context.get(CONF_NAME)
        return self.async_show_form(
            step_id="zeroconf_confirm",
            description_placeholders={"name": name},
            errors=errors or {},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        return OpenEVSEOptionsFlow(config_entry)


class OpenEVSEOptionsFlow(OptionsFlow):
    """Options flow for KeyMaster."""

    def __init__(self, config_entry: ConfigEntry):
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
    prepare: bool = False,
) -> FlowResult:
    """Start a config flow."""
    errors = {}
    description_placeholders = {}
    source = cls.context.get("source")

    if user_input is None and not prepare:
        if source == SOURCE_ZEROCONF:
            return cls._show_confirm_dialog()
        return _show_config_form(
            cls,
            step_id,
            user_input,
            errors,
            description_placeholders,
            defaults,
            entry_id,
        )

    if user_input is not None:
        if source == SOURCE_ZEROCONF:
            user_input[CONF_HOST] = cls.context.get(CONF_HOST)
            user_input[CONF_ID] = cls.context.get(CONF_ID)
            user_input[CONF_NAME] = cls.context.get(CONF_NAME)

            # Check if already configured
            await cls.async_set_unique_id(user_input[CONF_ID])
            cls._abort_if_unique_id_configured(
                updates={CONF_HOST: user_input[CONF_HOST]}
            )

        if prepare:
            return await cls.async_step_zeroconf_confirm()

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
