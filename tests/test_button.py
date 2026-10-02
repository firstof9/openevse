"""Test OpenEVSE button platform."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN
from homeassistant.components.button import SERVICE_PRESS
from homeassistant.exceptions import HomeAssistantError
from openevsehttp.exceptions import CommandFailedError
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

    assert len(hass.states.async_entity_ids(BUTTON_DOMAIN)) == 5

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
    manager.add_rfid_tag = AsyncMock()
    manager.run_stuck_relay_recovery = AsyncMock()
    manager.reset_energy_meter = AsyncMock()

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

    # 3. Test Learn RFID Tag Button
    entity_id = "button.openevse_learn_rfid_tag"
    state = hass.states.get(entity_id)
    assert state

    await hass.services.async_call(
        BUTTON_DOMAIN, SERVICE_PRESS, {"entity_id": entity_id}, blocking=True
    )

    assert manager.add_rfid_tag.called
    assert manager.add_rfid_tag.call_count == 1

    # 4. Test Stuck-Relay Recovery Button
    entity_id = "button.openevse_stuck_relay_recovery"
    state = hass.states.get(entity_id)
    assert state
    assert (
        state.state == "unavailable"
    )  # Default test charger has controller firmware 7.1.3 < 9.3.0

    with patch.object(manager, "controller_version_check", return_value=True):
        coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        coordinator.async_update_listeners()
        await hass.async_block_till_done()

        await hass.services.async_call(
            BUTTON_DOMAIN, SERVICE_PRESS, {"entity_id": entity_id}, blocking=True
        )

        assert manager.run_stuck_relay_recovery.called
        assert manager.run_stuck_relay_recovery.call_count == 1

    # 5. Test Reset Energy Meter Button (soft reset: hard=False, import_from_evse=False)
    entity_id = "button.openevse_reset_energy_meter"
    state = hass.states.get(entity_id)
    assert state

    await hass.services.async_call(
        BUTTON_DOMAIN, SERVICE_PRESS, {"entity_id": entity_id}, blocking=True
    )

    assert manager.reset_energy_meter.called
    assert manager.reset_energy_meter.call_count == 1
    manager.reset_energy_meter.assert_awaited_once_with(
        hard=False, import_from_evse=False
    )


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
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            BUTTON_DOMAIN, SERVICE_PRESS, {"entity_id": entity_id}, blocking=True
        )

    assert "Error connecting to device" in caplog.text


async def test_buttons_command_failed_error(
    hass,
    test_charger,
    mock_ws_start,
    mock_aioclient,
    caplog,
):
    """Test button press raises HomeAssistantError on CommandFailedError."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    manager = hass.data[DOMAIN][entry.entry_id]["manager"]
    manager.restart_wifi = AsyncMock(
        side_effect=CommandFailedError("Failed to restart WiFi: restart gateway")
    )

    entity_id = "button.openevse_restart_wifi"
    with pytest.raises(HomeAssistantError, match="Command failed for Restart WiFi"):
        await hass.services.async_call(
            BUTTON_DOMAIN, SERVICE_PRESS, {"entity_id": entity_id}, blocking=True
        )

    assert "Command failed for button [restart_wifi]" in caplog.text


async def test_button_version_availability(
    hass,
    test_charger,
    mock_ws_start,
    mock_aioclient,
):
    """Test button availability based on firmware version."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entity_id = "button.openevse_learn_rfid_tag"
    state = hass.states.get(entity_id)
    assert state
    assert state.state != "unavailable"

    manager = hass.data[DOMAIN][entry.entry_id]["manager"]
    with patch.object(manager, "version_check", return_value=False):
        coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        coordinator.async_update_listeners()
        await hass.async_block_till_done()

        state = hass.states.get(entity_id)
        assert state
        assert state.state == "unavailable"

    with patch.object(manager, "version_check", return_value=True):
        coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        coordinator.async_update_listeners()
        await hass.async_block_till_done()

        state = hass.states.get(entity_id)
        assert state
        assert state.state != "unavailable"

    # Test controller version check on stuck_relay_recovery button
    entity_id_relay = "button.openevse_stuck_relay_recovery"
    state_relay = hass.states.get(entity_id_relay)
    assert state_relay
    assert state_relay.state == "unavailable"

    with patch.object(manager, "controller_version_check", return_value=True):
        coordinator.async_update_listeners()
        await hass.async_block_till_done()

        state_relay = hass.states.get(entity_id_relay)
        assert state_relay
        assert state_relay.state != "unavailable"

    with patch.object(manager, "controller_version_check", return_value=False):
        coordinator.async_update_listeners()
        await hass.async_block_till_done()

        state_relay = hass.states.get(entity_id_relay)
        assert state_relay
        assert state_relay.state == "unavailable"
