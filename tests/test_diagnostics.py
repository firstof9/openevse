"""Test the OpenEVSE diagnostics."""

from unittest.mock import patch

import pytest
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openevse.const import DOMAIN
from custom_components.openevse.diagnostics import (
    async_get_config_entry_diagnostics,
    async_get_device_diagnostics,
)
from tests.const import DIAG_CONFIG_DATA, DIAG_DEVICE_RESULTS


@pytest.mark.asyncio
async def test_config_entry_diagnostics(hass, test_charger, mock_ws_start):
    """Test the config entry level diagnostics data dump."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="imap.test.email",
        data=DIAG_CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    result = await async_get_config_entry_diagnostics(hass, entry)

    assert isinstance(result, dict)
    assert result["config"]["data"][CONF_HOST] == "openevse.test.tld"
    assert result["config"]["data"][CONF_PASSWORD] == "**REDACTED**"
    assert result["config"]["data"][CONF_USERNAME] == "testuser"


@pytest.mark.asyncio
async def test_device_diagnostics(hass, test_charger, mock_ws_start):
    """Test the device level diagnostics data dump."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="openevse",
        data=DIAG_CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await async_get_device_diagnostics(hass, entry, None)

    assert result == DIAG_DEVICE_RESULTS
