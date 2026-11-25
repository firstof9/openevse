"""Test openevse binary sensors."""

import logging

import pytest
from homeassistant.components.binary_sensor import (
    DOMAIN as BINARY_SENSOR_DOMAIN,
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntityDescription,
)
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openevse.binary_sensor import OpenEVSEBinarySensor
from custom_components.openevse.const import DOMAIN

from .conftest import enable_entities_and_reload
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

    # 1. Test Shaper Updated
    entity_id = "binary_sensor.openevse_shaper_updated"
    await enable_entities_and_reload(
        hass, entity_registry, entry, BINARY_SENSOR_DOMAIN, entity_id
    )

    state = hass.states.get(entity_id)
    assert state.state == "on"

    # 2. Test Vehicle Connected
    state = hass.states.get("binary_sensor.openevse_vehicle_connected")
    assert state
    assert state.state == "off"

    # 3. Test Manual Override
    state = hass.states.get("binary_sensor.openevse_manual_override")
    assert state
    assert state.state == "off"

    # 4. Test MQTT Connected
    entity_id = "binary_sensor.openevse_mqtt_connected"
    await enable_entities_and_reload(
        hass, entity_registry, entry, BINARY_SENSOR_DOMAIN, entity_id
    )

    state = hass.states.get(entity_id)
    assert state
    assert state.state == "on"


async def test_binary_sensors_v2(
    hass,
    test_charger_v2,
    mock_ws_start,
    mock_aioclient,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test binary_sensors on v2 firmware."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    with caplog.at_level(logging.DEBUG):
        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 4
        entries = hass.config_entries.async_entries(DOMAIN)
        assert len(entries) == 1

        assert DOMAIN in hass.config.components

        entity_id = "binary_sensor.openevse_divert_active"
        state = hass.states.get(entity_id)
        assert state
        assert state.state == "off"


async def test_binary_sensor_coverage_gaps(hass, test_charger, mock_ws_start):
    """Test binary_sensor coverage gaps."""
    entry = MockConfigEntry(domain=DOMAIN, data=CONFIG_DATA)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    coordinator = entry.runtime_data.coordinator

    # Test is_on property when sensor type is missing from coordinator data
    description_bin = BinarySensorEntityDescription(
        key="missing_bin", name="Missing Bin"
    )
    bin_sensor = OpenEVSEBinarySensor(description_bin, coordinator, entry)
    coordinator.data = {}
    assert bin_sensor.is_on is None
