"""Test openevse switches."""

import logging

import pytest
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openevse.const import DOMAIN, COORDINATOR

from .const import CONFIG_DATA
from .conftest import TEST_URL_CONFIG

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
