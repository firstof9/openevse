"""Test openevse sensors."""

from unittest.mock import patch

import pytest

from custom_components.openevse.const import DOMAIN

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .const import CONFIG_DATA

pytestmark = pytest.mark.asyncio

CHARGER_NAME = "openevse"


async def test_sensors(hass, test_charger, mock_ws_start):
    """Test setup_entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 20
    assert len(hass.states.async_entity_ids(SWITCH_DOMAIN)) == 3
    assert len(hass.states.async_entity_ids(SELECT_DOMAIN)) == 2
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1

    assert DOMAIN in hass.config.components

    state = hass.states.get("sensor.openevse_wifi_firmware_version")
    assert state
    assert state.state == "4.1.2"
    state = hass.states.get("sensor.openevse_charge_time_elapsed")
    assert state
    assert state.state == "4.1"
    state = hass.states.get("sensor.openevse_total_usage")
    assert state
    assert state.state == "64.582"
