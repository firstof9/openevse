"""Test openevse switches."""

import logging
from asyncio import TimeoutError
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openevse.const import COORDINATOR, DOMAIN, MANAGER
from custom_components.openevse.switch import OpenEVSESwitch

from .conftest import TEST_URL_CONFIG
from .const import CONFIG_DATA

pytestmark = pytest.mark.asyncio

CHARGER_NAME = "openevse"
TEST_URL_OVERRIDE = "http://openevse.test.tld/override"
TEST_URL_DIVERT = "http://openevse.test.tld/divertmode"


async def test_switches(
    hass,
    test_charger,
    mock_ws_start,
    mock_aioclient,
):
    """Test standard switches."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Ensure all switches are created
    assert len(hass.states.async_entity_ids(SWITCH_DOMAIN)) == 4

    # Get the coordinator to simulate data updates
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    # -------------------------------------------------------------------------
    # 1. Test Sleep Mode Switch
    # -------------------------------------------------------------------------
    # Initial State: In CHARGER_DATA, "state" is "Sleeping", so switch should be ON.
    entity_id = "switch.openevse_sleep_mode"
    state = hass.states.get(entity_id)
    assert state
    assert state.state == "on"

    # Action: Turn Off (Wake up)
    mock_aioclient.post(
        TEST_URL_OVERRIDE,
        status=200,
        body='{"msg": "OK"}',
    )

    await hass.services.async_call(
        SWITCH_DOMAIN, "turn_off", {"entity_id": entity_id}, blocking=True
    )

    # Simulate the update that occurs after the command
    coordinator._data["state"] = "active"
    coordinator.async_set_updated_data(coordinator._data)
    await hass.async_block_till_done()

    # Assert: Entity should now be OFF (not sleeping)
    state = hass.states.get(entity_id)
    assert state.state == "off"

    # -------------------------------------------------------------------------
    # 2. Test Manual Override Switch
    # -------------------------------------------------------------------------
    # Initial State: In CHARGER_DATA, "manual_override" is False, so switch is OFF.
    entity_id = "switch.openevse_manual_override"
    state = hass.states.get(entity_id)
    assert state
    assert state.state == "off"

    # Action: Turn On
    mock_aioclient.post(
        TEST_URL_CONFIG,
        status=200,
        body='{"msg": "OK"}',
    )

    # Action: Turn On
    await hass.services.async_call(
        SWITCH_DOMAIN, "turn_on", {"entity_id": entity_id}, blocking=True
    )

    # Simulate update
    coordinator._data["manual_override"] = True
    coordinator.async_set_updated_data(coordinator._data)
    await hass.async_block_till_done()

    # Assert: Entity should now be ON
    state = hass.states.get(entity_id)
    assert state.state == "on"

    # -------------------------------------------------------------------------
    # 3. Test Solar PV Divert Switch
    # -------------------------------------------------------------------------
    # Initial State: In CHARGER_DATA, "divert_active" is False, so switch is OFF.
    entity_id = "switch.openevse_solar_pv_divert"
    state = hass.states.get(entity_id)
    assert state.state == "off"

    mock_aioclient.post(
        TEST_URL_DIVERT,
        status=200,
        body='{"msg": "OK"}',
    )

    # Action: Turn On
    await hass.services.async_call(
        SWITCH_DOMAIN, "turn_on", {"entity_id": entity_id}, blocking=True
    )

    # Simulate update
    coordinator._data["divert_active"] = True
    coordinator.async_set_updated_data(coordinator._data)
    await hass.async_block_till_done()

    # Assert: Entity should now be ON
    state = hass.states.get(entity_id)
    assert state.state == "on"


async def test_switches_v2(
    hass,
    test_charger_v2,
    mock_ws_start,
    mock_aioclient,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test switches on v2 firmware."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    with caplog.at_level(logging.DEBUG):
        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        assert len(hass.states.async_entity_ids(SWITCH_DOMAIN)) == 4
        entries = hass.config_entries.async_entries(DOMAIN)
        assert len(entries) == 1

        assert DOMAIN in hass.config.components

        entity_id = "switch.openevse_solar_pv_divert"
        state = hass.states.get(entity_id)
        assert state
        assert state.state == "unavailable"


async def test_switch_coverage_gaps(hass, test_charger, mock_ws_start):
    """Test switch coverage gaps."""
    entry = MockConfigEntry(domain=DOMAIN, data=CONFIG_DATA)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    manager = hass.data[DOMAIN][entry.entry_id][MANAGER]

    # Test is_on when data is missing
    description = MagicMock(
        key="missing_switch", name="Missing", toggle_command="test", min_version=None
    )
    switch = OpenEVSESwitch(hass, entry, coordinator, description, manager)
    assert switch.is_on is None

    # Test toggling of claim-based switches
    description_claim = MagicMock(
        key="state", name="Claim", toggle_command="claim", min_version=None
    )
    switch_claim = OpenEVSESwitch(hass, entry, coordinator, description_claim, manager)

    # turn_on -> release_claim (if current state is not sleeping)
    coordinator.data["state"] = "active"  # is_on = False
    with patch.object(manager, "release_claim") as mock_release:
        await switch_claim.async_turn_on()
        mock_release.assert_called_once()

    # turn_off -> make_claim (if current state is sleeping)
    coordinator.data["state"] = "sleeping"  # is_on = True
    with patch.object(manager, "make_claim") as mock_make:
        await switch_claim.async_turn_off()
        mock_make.assert_called_once_with(state="active")

    # Test early returns when switch is already in desired state
    coordinator.data["state"] = "sleeping"  # is_on = True
    with patch.object(manager, "release_claim") as mock_release:
        await switch_claim.async_turn_on()
        mock_release.assert_not_called()

    coordinator.data["state"] = "active"  # is_on = False
    with patch.object(manager, "make_claim") as mock_make:
        await switch_claim.async_turn_off()
        mock_make.assert_not_called()


async def test_switch_connection_error(
    hass,
    test_charger,
    mock_ws_start,
    mock_aioclient,
    caplog,
):
    """Test switch platform with connection error."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    manager = hass.data[DOMAIN][entry.entry_id]["manager"]
    manager.toggle_override = AsyncMock(side_effect=TimeoutError)

    entity_id = "switch.openevse_sleep_mode"

    # Force switch to different state to bypass 'if is_on' check
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    coordinator.data["state"] = "active"  # switch is OFF
    coordinator.async_set_updated_data(coordinator.data)
    await hass.async_block_till_done()

    # Test turn_on error
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            SWITCH_DOMAIN,
            "turn_on",
            {"entity_id": entity_id},
            blocking=True,
        )
    assert "Error connecting to device" in caplog.text
    caplog.clear()

    # Force switch to ON
    coordinator.data["state"] = "sleeping"  # switch is ON
    coordinator.async_set_updated_data(coordinator.data)
    await hass.async_block_till_done()

    # Test turn_off error
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            SWITCH_DOMAIN,
            "turn_off",
            {"entity_id": entity_id},
            blocking=True,
        )
    assert "Error connecting to device" in caplog.text
