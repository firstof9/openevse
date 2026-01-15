"""Test openevse sensors."""

import json
import logging
from datetime import datetime
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


async def test_sensors(
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
    with caplog.at_level(logging.DEBUG):
        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 23
        entries = hass.config_entries.async_entries(DOMAIN)
        assert len(entries) == 1

        assert DOMAIN in hass.config.components

        state = hass.states.get("sensor.openevse_wifi_firmware_version")
        assert state
        assert state.state == "v5.1.2"
        state = hass.states.get("sensor.openevse_charge_time_elapsed")
        assert state
        assert state.state == "4.1"
        state = hass.states.get("sensor.openevse_total_usage")
        assert state
        assert state.state == "64.582"
        state = hass.states.get("sensor.openevse_max_current")
        assert state
        assert state.state == "48"

        state = hass.states.get("sensor.openevse_override_state")
        assert state
        assert state.state == "auto"

        state = hass.states.get("sensor.openevse_charging_status")
        assert state
        assert state.attributes.get("icon") == "mdi:sleep"

        state = hass.states.get("sensor.openevse_current_power_usage_actual")
        assert state
        assert state.state == "0"

        # enable disabled sensor
        entity_id = "sensor.openevse_vehicle_charge_completion"
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
        assert await hass.config_entries.async_forward_entry_unload(entry, "sensor")
        await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
        await hass.async_block_till_done()

        state = hass.states.get("sensor.openevse_vehicle_charge_completion")
        assert state
        parsed_date = dt_util.parse_datetime(state.state)
        assert isinstance(parsed_date, datetime)


async def test_sensors_v2(
    hass,
    test_charger_v2,
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
    with caplog.at_level(logging.DEBUG):
        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 23
        entries = hass.config_entries.async_entries(DOMAIN)
        assert len(entries) == 1

        assert DOMAIN in hass.config.components

        state = hass.states.get("sensor.openevse_wifi_firmware_version")
        assert state
        assert state.state == "2.9.1"
        state = hass.states.get("sensor.openevse_charge_time_elapsed")
        assert state
        assert state.state == "145.85"
        state = hass.states.get("sensor.openevse_total_usage")
        assert state
        assert state.state == "1585.443"
        state = hass.states.get("sensor.openevse_max_current")
        assert state
        assert state.state == "unknown"

        state = hass.states.get("sensor.openevse_override_state")
        assert state
        assert state.state == "unavailable"

        state = hass.states.get("sensor.openevse_charging_status")
        assert state
        assert state.attributes.get("icon") == "mdi:power-plug-off"

        state = hass.states.get("sensor.openevse_override_state")
        assert state
        assert state.state == "unavailable"


async def test_sensors_new(
    hass,
    test_charger_new,
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
    with caplog.at_level(logging.DEBUG):
        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 23
        entries = hass.config_entries.async_entries(DOMAIN)
        assert len(entries) == 1

        assert DOMAIN in hass.config.components

        state = hass.states.get("sensor.openevse_wifi_firmware_version")
        assert state
        assert state.state == "v5.1.2"
        state = hass.states.get("sensor.openevse_charge_time_elapsed")
        assert state
        assert state.state == "0.0"
        state = hass.states.get("sensor.openevse_total_usage")
        assert state
        assert state.state == "20.12722817"
        state = hass.states.get("sensor.openevse_max_current")
        assert state
        assert state.state == "48"

        state = hass.states.get("sensor.openevse_override_state")
        assert state
        assert state.state == "auto"

        state = hass.states.get("sensor.openevse_charging_status")
        assert state
        assert state.attributes.get("icon") == "mdi:sleep"

        state = hass.states.get("sensor.openevse_current_power_usage_actual")
        assert state
        assert state.state == "4500"

        # enable disabled sensor
        entity_id = "sensor.openevse_vehicle_charge_completion"
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
        assert await hass.config_entries.async_forward_entry_unload(entry, "sensor")
        await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
        await hass.async_block_till_done()

        state = hass.states.get("sensor.openevse_vehicle_charge_completion")
        assert state
        assert state.state == "unknown"
