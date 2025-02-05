"""Test openevse sensors."""

import json
from datetime import timedelta
from unittest.mock import patch

import pytest
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openevse.const import DOMAIN

from .const import CONFIG_DATA

pytestmark = pytest.mark.asyncio

CHARGER_NAME = "openevse"
TEST_URL_OVERRIDE = "http://openevse.test.tld/override"


async def test_binary_sensors(
    hass,
    test_charger_new,
    mock_ws_start,
    mock_aioclient,
    entity_registry: er.EntityRegistry,
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

    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 22
    assert len(hass.states.async_entity_ids(SWITCH_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SELECT_DOMAIN)) == 2
    assert len(hass.states.async_entity_ids(NUMBER_DOMAIN)) == 1
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1

    assert DOMAIN in hass.config.components

    # enable disabled sensor
    entity_id = "binary_sensor.openevse_shaper_updated"
    entity_entry = entity_registry.async_get(entity_id)

    assert entity_entry
    assert entity_entry.disabled
    assert entity_entry.disabled_by is er.RegistryEntryDisabler.INTEGRATION

    updated_entry = entity_registry.async_update_entity(
        entity_entry.entity_id, disabled_by=None
    )
    assert updated_entry != entity_entry
    assert updated_entry.disabled is False

    # reload the integration
    assert await hass.config_entries.async_forward_entry_unload(entry, "binary_sensor")
    await hass.config_entries.async_forward_entry_setups(entry, ["binary_sensor"])
    await hass.async_block_till_done()

    state = hass.states.get(entity_id)
    assert state
    assert state.state == "on"
