"""Test OpenEVSE button platform."""

from asyncio import TimeoutError
from unittest.mock import AsyncMock

import pytest
from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN
from homeassistant.components.button import SERVICE_PRESS
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openevse.const import DOMAIN

from .const import CONFIG_DATA

pytestmark = pytest.mark.asyncio

CHARGER_NAME = "openevse"


async def test_buttons(
    hass,
    test_charger,
    mock_ws_start,
    mock_aioclient,
):
    """Test button entity setup and services."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(BUTTON_DOMAIN)) == 2

    # 1. Test Restart WiFi Button
    entity_id = "button.openevse_restart_wifi"
    state = hass.states.get(entity_id)
    assert state
    assert state.state == "unknown"  # Buttons are usually 'unknown' state

    # We need to mock the manager method to verify it's called.
    # Since test_charger is a real object (OpenEVSE), we can mock the method on the instance  # noqa: E501
    # stored in hass.data.
    manager = hass.data[DOMAIN][entry.entry_id]["manager"]

    # Using the standard mock approach for the method on the live object

    manager.restart_wifi = AsyncMock()
    manager.restart_evse = AsyncMock()

    await hass.services.async_call(
        BUTTON_DOMAIN, SERVICE_PRESS, {"entity_id": entity_id}, blocking=True
    )

    assert manager.restart_wifi.called
    assert manager.restart_wifi.call_count == 1

    # 2. Test Restart EVSE Button
    entity_id = "button.openevse_restart_evse"
    state = hass.states.get(entity_id)
    assert state

    await hass.services.async_call(
        BUTTON_DOMAIN, SERVICE_PRESS, {"entity_id": entity_id}, blocking=True
    )

    assert manager.restart_evse.called
    assert manager.restart_evse.call_count == 1


async def test_buttons_connection_error(
    hass,
    test_charger,
    mock_ws_start,
    mock_aioclient,
    caplog,
):
    """Test button platform with connection error."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    manager = hass.data[DOMAIN][entry.entry_id]["manager"]
    manager.restart_wifi = AsyncMock(side_effect=TimeoutError)

    entity_id = "button.openevse_restart_wifi"
    await hass.services.async_call(
        BUTTON_DOMAIN, SERVICE_PRESS, {"entity_id": entity_id}, blocking=True
    )

    assert "Error connecting to device" in caplog.text
