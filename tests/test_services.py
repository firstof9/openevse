"""Test openevse services."""

import json
import logging
from unittest.mock import patch

import pytest
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openevse.const import (
    ATTR_DEVICE_ID,
    ATTR_STATE,
    ATTR_TYPE,
    ATTR_VALUE,
    DOMAIN,
    SERVICE_CLEAR_LIMIT,
    SERVICE_CLEAR_OVERRIDE,
    SERVICE_GET_LIMIT,
    SERVICE_LIST_CLAIMS,
    SERVICE_LIST_OVERRIDES,
    SERVICE_MAKE_CLAIM,
    SERVICE_RELEASE_CLAIM,
    SERVICE_SET_LIMIT,
    SERVICE_SET_OVERRIDE,
)

from .const import CONFIG_DATA

pytestmark = pytest.mark.asyncio

CHARGER_NAME = "openevse"
TEST_URL_CLAIMS = "http://openevse.test.tld/claims"
TEST_URL_LIMIT = "http://openevse.test.tld/limit"
TEST_URL_OVERRIDE = "http://openevse.test.tld/override"


async def test_list_claims(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test setup_entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(
        TEST_URL_CLAIMS,
        status=200,
        body='[{"client": 4, "priority": 500, "state": "disabled", "auto_release": true}, {"client": 65538, "priority": 50, "state": "active", "charge_current": 7, "auto_release": false}]',
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        body="{}",
        repeat=True,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    # setup service call
    with caplog.at_level(logging.DEBUG):
        response = await hass.services.async_call(
            DOMAIN,
            SERVICE_LIST_CLAIMS,
            {ATTR_DEVICE_ID: entry.device_id},
            blocking=True,
            return_response=True,
        )
        assert response == {
            0: {
                "client": 4,
                "priority": 500,
                "state": "disabled",
                "auto_release": True,
            },
            1: {
                "client": 65538,
                "priority": 50,
                "state": "active",
                "charge_current": 7,
                "auto_release": False,
            },
        }


async def test_make_claim(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test release claim service call."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.post(
        f"{TEST_URL_CLAIMS}/20",
        status=200,
        body='[{"msg":"done"}]',
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        body="{}",
        repeat=True,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    # setup service call
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_MAKE_CLAIM,
            {
                ATTR_DEVICE_ID: entry.device_id,
                ATTR_STATE: "active",
            },
            blocking=True,
        )
        assert "Make claim response:" in caplog.text


async def test_release_claim(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test release claim service call."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.delete(
        f"{TEST_URL_CLAIMS}/20",
        status=200,
        body='[{"msg":"done"}]',
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        body="{}",
        repeat=True,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    # setup service call
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_RELEASE_CLAIM,
            {ATTR_DEVICE_ID: entry.device_id},
            blocking=True,
        )
        assert "Release claim command sent." in caplog.text


async def test_get_limit(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test setup_entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(
        TEST_URL_LIMIT,
        status=200,
        body='{"type": "energy", "value": 10}',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        body="{}",
        repeat=True,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    # setup service call
    with caplog.at_level(logging.DEBUG):
        response = await hass.services.async_call(
            DOMAIN,
            SERVICE_GET_LIMIT,
            {ATTR_DEVICE_ID: entry.device_id},
            blocking=True,
            return_response=True,
        )
        assert response == {"type": "energy", "value": 10}


async def test_clear_limit(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test setup_entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.delete(
        TEST_URL_LIMIT,
        status=200,
        body='{"msg": "Deleted"}',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        body="{}",
        repeat=True,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    # setup service call
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_CLEAR_LIMIT,
            {ATTR_DEVICE_ID: entry.device_id},
            blocking=True,
        )
        assert "Limit clear command sent." in caplog.text


async def test_set_limit(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test setup_entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.post(
        TEST_URL_LIMIT,
        status=200,
        body='{"msg": "OK"}',
        repeat=True,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        body="{}",
        repeat=True,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    # setup service call
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_LIMIT,
            {
                ATTR_DEVICE_ID: entry.device_id,
                ATTR_TYPE: "range",
                ATTR_VALUE: "50",
            },
            blocking=True,
        )
        assert "Set Limit response:" in caplog.text


async def test_clear_override(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test release claim service call."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.delete(
        TEST_URL_OVERRIDE,
        status=200,
        body='{"msg": "OK"}',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        body="{}",
        repeat=True,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    # setup service call
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_CLEAR_OVERRIDE,
            {ATTR_DEVICE_ID: entry.device_id},
            blocking=True,
        )
        assert "Override clear command sent." in caplog.text


async def test_list_overrides(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test setup_entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    value = {
        "state": "active",
        "charge_current": 0,
        "max_current": 0,
        "energy_limit": 0,
        "time_limit": 0,
        "auto_release": True,
    }
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        body=json.dumps(value),
        repeat=True,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    # setup service call
    with caplog.at_level(logging.DEBUG):
        response = await hass.services.async_call(
            DOMAIN,
            SERVICE_LIST_OVERRIDES,
            {ATTR_DEVICE_ID: entry.device_id},
            blocking=True,
            return_response=True,
        )
        assert response == value


async def test_set_override(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test release claim service call."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.post(
        TEST_URL_OVERRIDE,
        status=200,
        body='{"msg": "OK"}',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        body="{}",
        repeat=True,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    # setup service call
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_OVERRIDE,
            {
                ATTR_DEVICE_ID: entry.device_id,
                ATTR_STATE: "disabled",
            },
            blocking=True,
        )
        assert "Set Override response:" in caplog.text
