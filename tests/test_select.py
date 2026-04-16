"""Test openevse select entities."""

import logging
from asyncio import TimeoutError
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.select import SERVICE_SELECT_OPTION
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openevse import CommandFailedError, InvalidValueError
from custom_components.openevse.const import COORDINATOR, DOMAIN, MANAGER
from custom_components.openevse.entity import OpenEVSESelectEntityDescription
from custom_components.openevse.select import OpenEVSESelect

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
        assert state is not None
        assert state.state == "unavailable"


async def test_select_coverage_gaps(hass, test_charger, mock_ws_start):
    """Test select coverage gaps."""
    entry = MockConfigEntry(domain=DOMAIN, data=CONFIG_DATA)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    manager = hass.data[DOMAIN][entry.entry_id][MANAGER]

    # Test current_option when data is missing
    description = OpenEVSESelectEntityDescription(
        key="missing_type", name="Missing", options=["a", "b"]
    )
    select = OpenEVSESelect(hass, entry, coordinator, description, manager)
    assert select.current_option is None

    # Test commands starting with $
    description_dollar = OpenEVSESelectEntityDescription(
        key="test", name="Test", command="$SC", options=["1", "2"]
    )
    select_dollar = OpenEVSESelect(
        hass, entry, coordinator, description_dollar, manager
    )
    with patch(
        "custom_components.openevse.select.send_command", new_callable=AsyncMock
    ) as mock_send:
        await select_dollar.async_select_option("2")
        mock_send.assert_awaited_once_with(manager, "$SC 2")

    # Test availability when no data is present
    coordinator.data = None
    assert select.available is False

    # Test get_options for max_current_soft when data is missing
    description_max = OpenEVSESelectEntityDescription(
        key="max_current_soft",
        name="Charge Rate",
        default_options=["6", "48"],
    )
    select_max = OpenEVSESelect(hass, entry, coordinator, description_max, manager)
    assert select_max.options == ["6", "48"]

    # Test get_options for max_current_soft when data and default_options are missing
    description_no_default = OpenEVSESelectEntityDescription(
        key="max_current_soft",
        name="Charge Rate",
        default_options=None,
    )
    coordinator.data = None
    select_no_default = OpenEVSESelect(
        hass, entry, coordinator, description_no_default, manager
    )
    assert "6" in select_no_default.options
    assert "48" in select_no_default.options


async def test_select_get_options_edge_cases(hass, test_charger, mock_ws_start):
    """Test get_options edge cases for malformed data."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    select_desc = OpenEVSESelectEntityDescription(
        key="max_current_soft",
        name="Charge Rate",
    )
    entity = OpenEVSESelect(hass, entry, coordinator, select_desc, test_charger)

    # 1. Malformed min_amps (string)
    coordinator.data = {"min_amps": "invalid", "max_amps": 40}
    options = entity.get_options()
    assert options[0] == "6"

    # 2. Malformed max_amps (string)
    coordinator.data = {"min_amps": 10, "max_amps": "invalid"}
    options = entity.get_options()
    assert options[-1] == "48"

    # 3. Both malformed
    coordinator.data = {"min_amps": "invalid", "max_amps": "invalid"}
    options = entity.get_options()
    assert options[0] == "6"
    assert options[-1] == "48"


async def test_select_connection_error(
    hass,
    test_charger,
    mock_ws_start,
    mock_aioclient,
    caplog,
):
    """Test select platform with connection error."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    manager = hass.data[DOMAIN][entry.entry_id]["manager"]
    manager.set_divert_mode = AsyncMock(side_effect=TimeoutError)

    entity_id = "select.openevse_divert_mode"

    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {"entity_id": entity_id, "option": "fast"},
        blocking=True,
    )
    assert "Error connecting to device" in caplog.text
