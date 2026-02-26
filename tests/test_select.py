"""Test openevse select entities."""

import logging
from unittest.mock import patch

import pytest
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.select import SERVICE_SELECT_OPTION
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openevse import CommandFailedError, InvalidValueError
from custom_components.openevse.const import COORDINATOR, DOMAIN

from .const import CONFIG_DATA

pytestmark = pytest.mark.asyncio

CHARGER_NAME = "openevse"
TEST_URL_CLAIMS = "http://openevse.test.tld/claims"
TEST_URL_LIMIT = "http://openevse.test.tld/limit"
TEST_URL_OVERRIDE = "http://openevse.test.tld/override"
TEST_URL_DIVERT = "http://openevse.test.tld/divertmode"


async def test_select(
    hass,
    test_charger,
    mock_ws_start,
    mock_aioclient,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test setup_entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(SELECT_DOMAIN)) == 3
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1

    assert DOMAIN in hass.config.components

    entity_id = "select.openevse_override_state"

    state = hass.states.get(entity_id)
    assert state
    assert state.state == "auto"

    servicedata = {
        "entity_id": entity_id,
        "option": "disabled",
    }

    await hass.services.async_call(
        SELECT_DOMAIN, SERVICE_SELECT_OPTION, servicedata, blocking=True
    )
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    coordinator._data["override_state"] = "disabled"
    updated_data = coordinator._data
    coordinator.async_set_updated_data(updated_data)
    await hass.async_block_till_done()

    state = hass.states.get(entity_id)
    assert state
    assert state.state == "disabled"

    mock_aioclient.delete(
        TEST_URL_OVERRIDE,
        status=200,
        body='{"msg": "OK"}',
    )

    servicedata = {
        "entity_id": entity_id,
        "option": "auto",
    }

    await hass.services.async_call(
        SELECT_DOMAIN, SERVICE_SELECT_OPTION, servicedata, blocking=True
    )
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    coordinator._data["override_state"] = "auto"
    updated_data = coordinator._data
    coordinator.async_set_updated_data(updated_data)
    await hass.async_block_till_done()

    state = hass.states.get(entity_id)
    assert state
    assert state.state == "auto"

    servicedata = {
        "entity_id": entity_id,
        "option": "active",
    }

    await hass.services.async_call(
        SELECT_DOMAIN, SERVICE_SELECT_OPTION, servicedata, blocking=True
    )
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    coordinator._data["override_state"] = "active"
    updated_data = coordinator._data
    coordinator.async_set_updated_data(updated_data)
    await hass.async_block_till_done()

    state = hass.states.get(entity_id)
    assert state
    assert state.state == "active"

    entity_id = "select.openevse_divert_mode"
    state = hass.states.get(entity_id)
    assert state
    assert state.state == "eco"

    value = "Divert Mode changed"
    mock_aioclient.post(
        TEST_URL_DIVERT,
        status=200,
        body=value,
    )

    servicedata = {
        "entity_id": entity_id,
        "option": "fast",
    }
    await hass.services.async_call(
        SELECT_DOMAIN, SERVICE_SELECT_OPTION, servicedata, blocking=True
    )
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    coordinator._data["divertmode"] = "fast"
    updated_data = coordinator._data
    coordinator.async_set_updated_data(updated_data)
    await hass.async_block_till_done()

    state = hass.states.get(entity_id)
    assert state
    assert state.state == "fast"


async def test_select_max_current(
    hass,
    test_charger,
    mock_ws_start,
    mock_aioclient,
    entity_registry: er.EntityRegistry,
):
    """Test the Charge Rate (Max Current) select entity."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    entity_id = "select.openevse_charge_rate"
    state = hass.states.get(entity_id)

    assert state

    options = state.attributes.get("options")
    assert options is not None
    assert "6" in options
    assert "48" in options
    assert "49" not in options

    # Test selecting an option
    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {"entity_id": entity_id, "option": "24"},
        blocking=True,
    )


async def test_select_availability_divert(
    hass, test_charger, mock_ws_start, mock_aioclient, caplog
):
    """Test that charge rate select becomes unavailable when divert is active."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entity_id = "select.openevse_charge_rate"

    # Initial state should be available
    state = hass.states.get(entity_id)
    assert state.state != "unavailable"

    # Simulate PV Divert Active
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    with caplog.at_level(logging.DEBUG):
        coordinator._data["divert_active"] = True
        coordinator._data["divertmode"] = "eco"  # Ensure mode is eco
        coordinator.async_set_updated_data(coordinator._data)
        await hass.async_block_till_done()

    # State should now be unavailable
    state = hass.states.get(entity_id)
    assert state.state == "unavailable"


async def test_select_exceptions(
    hass,
    test_charger,
    mock_ws_start,
    mock_aioclient,
    caplog,
):
    """Test select exception handling."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entity_id = "select.openevse_divert_mode"

    # Access manager to mock method
    manager = hass.data[DOMAIN][entry.entry_id]["manager"]

    # 1. Test ValueError/KeyError
    with patch.object(manager, "set_divert_mode", side_effect=ValueError("Test Error")):
        await hass.services.async_call(
            SELECT_DOMAIN,
            SERVICE_SELECT_OPTION,
            {"entity_id": entity_id, "option": "fast"},
            blocking=True,
        )
        assert "Could not set status for" in caplog.text

    # 2. Test InvalidValueError
    with patch.object(manager, "set_divert_mode", side_effect=InvalidValueError):
        await hass.services.async_call(
            SELECT_DOMAIN,
            SERVICE_SELECT_OPTION,
            {"entity_id": entity_id, "option": "fast"},
            blocking=True,
        )
        assert "invalid for command" in caplog.text

    # 3. Test CommandFailedError
    with patch.object(manager, "set_divert_mode", side_effect=CommandFailedError):
        await hass.services.async_call(
            SELECT_DOMAIN,
            SERVICE_SELECT_OPTION,
            {"entity_id": entity_id, "option": "fast"},
            blocking=True,
        )
        assert "failed" in caplog.text


async def test_select_min_version(
    hass,
    test_charger,
    mock_ws_start,
):
    """Test select availability with old firmware."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )

    # Mock version check to return False (simulating old firmware)
    with patch("custom_components.openevse.OpenEVSE.version_check", return_value=False):
        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        # 'override_state' requires min_version 4.1.0, so it should be unavailable
        entity_id = "select.openevse_override_state"
        state = hass.states.get(entity_id)
        assert state.state == "unavailable"
