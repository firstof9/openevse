"""Test openevse services."""

import asyncio
import json
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import voluptuous as vol
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from openevsehttp.exceptions import CommandFailedError, ParseJSONError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openevse.const import (
    ATTR_AUTO_RELEASE,
    ATTR_CERTIFICATE,
    ATTR_CERTIFICATE_ID,
    ATTR_CHARGE_CURRENT,
    ATTR_DEVICE_ID,
    ATTR_ENERGY_LIMIT,
    ATTR_HARD,
    ATTR_IMPORT,
    ATTR_KEY,
    ATTR_MAX_CURRENT,
    ATTR_NAME,
    ATTR_NOTIFICATION_ID,
    ATTR_PERSON,
    ATTR_RFID,
    ATTR_SNTP,
    ATTR_STATE,
    ATTR_TIME,
    ATTR_TIME_LIMIT,
    ATTR_TIMEZONE,
    ATTR_TYPE,
    ATTR_VALUE,
    DOMAIN,
    MANAGER,
    SERVICE_ACK_NOTIFICATION,
    SERVICE_ADD_CERTIFICATE,
    SERVICE_ADD_RFID_TAG,
    SERVICE_CLEAR_LIMIT,
    SERVICE_CLEAR_OVERRIDE,
    SERVICE_DELETE_CERTIFICATE,
    SERVICE_DELETE_RFID_USER,
    SERVICE_GET_CERTIFICATES,
    SERVICE_GET_LIMIT,
    SERVICE_GET_NOTIFICATIONS,
    SERVICE_GET_RFID_USERS,
    SERVICE_GET_TIME,
    SERVICE_LIST_CLAIMS,
    SERVICE_LIST_OVERRIDES,
    SERVICE_MAKE_CLAIM,
    SERVICE_RELEASE_CLAIM,
    SERVICE_RESET_ENERGY_METER,
    SERVICE_SET_LIMIT,
    SERVICE_SET_OVERRIDE,
    SERVICE_SET_RFID_USER,
    SERVICE_SET_TIME,
    SERVICE_SYNC_TIME,
)

from .const import CONFIG_DATA

pytestmark = pytest.mark.asyncio

CHARGER_NAME = "openevse"
TEST_URL_CLAIMS = "http://openevse.test.tld/claims"
TEST_URL_LIMIT = "http://openevse.test.tld/limit"
TEST_URL_OVERRIDE = "http://openevse.test.tld/override"
TEST_URL_TIME = "http://openevse.test.tld/time"
TEST_URL_RFID_ADD = "http://openevse.test.tld/rfid/add"
TEST_URL_RFID_USERS = "http://openevse.test.tld/rfid/users"
TEST_URL_CERTIFICATES = "http://openevse.test.tld/certificates"
TEST_URL_NOTIFICATIONS = "http://openevse.test.tld/notifications"
TEST_URL_NOTIFICATIONS_ACK = "http://openevse.test.tld/notifications/ack"


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
        text='[{"client": 4, "priority": 500, "state": "disabled", "auto_release": true}, {"client": 65538, "priority": 50, "state": "active", "charge_current": 7, "auto_release": false}]',  # noqa: E501
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
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
        text='[{"msg":"done"}]',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
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
        text='[{"msg":"done"}]',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
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
        text='{"type": "energy", "value": 10}',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
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
        text='{"msg": "Deleted"}',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
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
        text='{"msg": "OK"}',
    )
    mock_aioclient.get(
        TEST_URL_LIMIT,
        status=200,
        text='{"type": "energy", "value": 10}',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
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
        text='{"msg": "OK"}',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
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


async def test_clear_override_not_active(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test release claim service call when no override is active."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.delete(
        TEST_URL_OVERRIDE,
        status=500,
        text='{"msg": "Failed to release manual override"}',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
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
        assert "No active override to clear." in caplog.text


async def test_clear_override_other_runtime_error(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
):
    """Test release claim service call with an unexpected RuntimeError."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    # Status code 500 with another message
    mock_aioclient.delete(
        TEST_URL_OVERRIDE,
        status=500,
        text='{"msg": "Some other server error"}',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    # setup service call, expects HomeAssistantError
    with pytest.raises(HomeAssistantError, match="Error communicating with device"):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_CLEAR_OVERRIDE,
            {ATTR_DEVICE_ID: entry.device_id},
            blocking=True,
        )


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
        text=json.dumps(value),
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
        text='{"msg": "OK"}',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
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


async def test_make_claim_with_arguments(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test make_claim service with all optional arguments."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    # Mock the specific claim endpoint with arguments
    mock_aioclient.post(
        f"{TEST_URL_CLAIMS}/20",
        status=200,
        text='[{"msg":"done"}]',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")

    # Call service with all arguments
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_MAKE_CLAIM,
            {
                ATTR_DEVICE_ID: entry.device_id,
                ATTR_STATE: "active",
                ATTR_CHARGE_CURRENT: 16,
                ATTR_MAX_CURRENT: 32,
                ATTR_AUTO_RELEASE: True,
            },
            blocking=True,
        )

        assert "Make claim response:" in caplog.text


async def test_set_override_all_args(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test set_override service with all arguments."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.post(
        TEST_URL_OVERRIDE,
        status=200,
        text='{"msg": "OK"}',
    )
    # Ensure get override is mocked to avoid errors during setup/teardown updates
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")

    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_OVERRIDE,
            {
                ATTR_DEVICE_ID: entry.device_id,
                ATTR_STATE: "active",
                ATTR_CHARGE_CURRENT: 16,
                ATTR_MAX_CURRENT: 32,
                ATTR_ENERGY_LIMIT: 1000,
                ATTR_TIME_LIMIT: 3600,
                ATTR_AUTO_RELEASE: False,
            },
            blocking=True,
        )
        assert "Set Override response:" in caplog.text


async def test_set_limit_auto_release(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test set_limit service with auto_release argument."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.post(
        TEST_URL_LIMIT,
        status=200,
        text='{"msg": "OK"}',
    )
    mock_aioclient.get(
        TEST_URL_LIMIT,
        status=200,
        text='{"type": "time", "value": 60, "auto_release": false}',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")

    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_LIMIT,
            {
                ATTR_DEVICE_ID: entry.device_id,
                ATTR_TYPE: "time",
                ATTR_VALUE: 60,
                ATTR_AUTO_RELEASE: False,
            },
            blocking=True,
        )
        assert "Set Limit response:" in caplog.text


async def test_get_time(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test get_time service."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(
        TEST_URL_TIME,
        status=200,
        text='{"time": "2026-03-25T15:30:00Z", "timezone": "UTC", "sntp": true}',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    with caplog.at_level(logging.DEBUG):
        response = await hass.services.async_call(
            DOMAIN,
            SERVICE_GET_TIME,
            {ATTR_DEVICE_ID: entry.device_id},
            blocking=True,
            return_response=True,
        )
        assert response == {
            "time": "2026-03-25T15:30:00Z",
            "timezone": "UTC",
            "sntp": True,
        }


async def test_set_time(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test set_time service."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.post(
        TEST_URL_TIME,
        status=200,
        text='{"msg": "OK"}',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_TIME,
            {
                ATTR_DEVICE_ID: entry.device_id,
                ATTR_TIME: "2026-03-25T15:30:00Z",
                ATTR_TIMEZONE: "Europe/London",
                ATTR_SNTP: False,
            },
            blocking=True,
        )
        assert "Set time command sent successfully." in caplog.text


async def test_set_time_no_parameters(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
):
    """Test set_time service fails validation when no parameters are provided."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    with pytest.raises(
        vol.Invalid, match="(must contain at least one of|at least one of)"
    ):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_TIME,
            {ATTR_DEVICE_ID: entry.device_id},
            blocking=True,
        )


async def test_sync_time(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test sync_time service."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.post(
        TEST_URL_TIME,
        status=200,
        text='{"msg": "OK"}',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SYNC_TIME,
            {ATTR_DEVICE_ID: entry.device_id},
            blocking=True,
        )
        assert "Sync time command sent successfully." in caplog.text


async def test_sync_time_parse_json_error(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test sync_time logs an error when the charger returns a non-JSON 400 response."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    manager = hass.data[DOMAIN][entry.config_entry_id][MANAGER]
    with (
        patch.object(manager, "sync_time", side_effect=ParseJSONError),
        caplog.at_level(logging.ERROR),
    ):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SYNC_TIME,
            {ATTR_DEVICE_ID: entry.device_id},
            blocking=True,
        )
        assert "Error parsing response from charger for sync_time" in caplog.text


async def test_set_time_parse_json_error(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test set_time logs an error when the charger returns a non-JSON response."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    manager = hass.data[DOMAIN][entry.config_entry_id][MANAGER]
    with (
        patch.object(manager, "set_time", side_effect=ParseJSONError),
        caplog.at_level(logging.ERROR),
    ):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_TIME,
            {ATTR_DEVICE_ID: entry.device_id, ATTR_SNTP: True},
            blocking=True,
        )
        assert "Error parsing response from charger for set_time" in caplog.text


async def test_get_time_parse_json_error(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test get_time returns empty dict and logs an error on ParseJSONError."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    manager = hass.data[DOMAIN][entry.config_entry_id][MANAGER]
    with (
        patch.object(manager, "get_time", side_effect=ParseJSONError),
        caplog.at_level(logging.ERROR),
    ):
        response = await hass.services.async_call(
            DOMAIN,
            SERVICE_GET_TIME,
            {ATTR_DEVICE_ID: entry.device_id},
            blocking=True,
            return_response=True,
        )
        assert response == {}
        assert "Error parsing response from charger for get_time" in caplog.text


async def test_add_rfid_tag(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test add_rfid_tag service."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.post(
        TEST_URL_RFID_ADD,
        status=200,
        text='{"msg": "OK"}',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_ADD_RFID_TAG,
            {ATTR_DEVICE_ID: entry.device_id},
            blocking=True,
        )
        assert "Add RFID tag command sent successfully." in caplog.text


async def test_set_rfid_user_with_name(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test set_rfid_user service with a name string."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.post(
        TEST_URL_RFID_USERS,
        status=200,
        text='{"msg": "OK"}',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_RFID_USER,
            {
                ATTR_DEVICE_ID: entry.device_id,
                ATTR_RFID: "01020304",
                ATTR_NAME: "Alice",
            },
            blocking=True,
        )
        assert "Set RFID user command sent successfully." in caplog.text


async def test_set_rfid_user_with_person(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test set_rfid_user service resolving person entity name."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.post(
        TEST_URL_RFID_USERS,
        status=200,
        text='{"msg": "OK"}',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Create a person state in hass
    hass.states.async_set("person.john_doe", "home", {"friendly_name": "John Doe"})

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_RFID_USER,
            {
                ATTR_DEVICE_ID: entry.device_id,
                ATTR_RFID: "DEADBEEF",
                ATTR_PERSON: "person.john_doe",
            },
            blocking=True,
        )
        assert "Set RFID user command sent successfully." in caplog.text

    # Test with a person state having no friendly_name
    hass.states.async_set("person.jane_doe", "home", {})
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_RFID_USER,
            {
                ATTR_DEVICE_ID: entry.device_id,
                ATTR_RFID: "CAFEBABE",
                ATTR_PERSON: "person.jane_doe",
            },
            blocking=True,
        )
        assert "Set RFID user command sent successfully." in caplog.text

    # Test with a person entity that doesn't exist in states (falls back to entity_id)
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_RFID_USER,
            {
                ATTR_DEVICE_ID: entry.device_id,
                ATTR_RFID: "12345678",
                ATTR_PERSON: "person.unknown",
            },
            blocking=True,
        )
        assert "Set RFID user command sent successfully." in caplog.text


async def test_set_rfid_user_no_name_or_person(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
):
    """Test set_rfid_user fails validation when neither name nor person is given."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    with pytest.raises(
        vol.Invalid, match="(must contain at least one of|at least one of)"
    ):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_RFID_USER,
            {
                ATTR_DEVICE_ID: entry.device_id,
                ATTR_RFID: "01020304",
            },
            blocking=True,
        )


async def test_delete_rfid_user(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test delete_rfid_user service."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.delete(
        f"{TEST_URL_RFID_USERS}?rfid=01020304",
        status=200,
        text='{"msg": "OK"}',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_DELETE_RFID_USER,
            {
                ATTR_DEVICE_ID: entry.device_id,
                ATTR_RFID: "01020304",
            },
            blocking=True,
        )
        assert "Delete RFID user command sent successfully." in caplog.text


async def test_get_rfid_users(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test get_rfid_users service."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(
        TEST_URL_RFID_USERS,
        status=200,
        text='{"01020304": "Alice", "DEADBEEF": "Bob"}',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    with caplog.at_level(logging.DEBUG):
        response = await hass.services.async_call(
            DOMAIN,
            SERVICE_GET_RFID_USERS,
            {ATTR_DEVICE_ID: entry.device_id},
            blocking=True,
            return_response=True,
        )
        assert response == {
            "users": {
                "01020304": "Alice",
                "DEADBEEF": "Bob",
            }
        }


async def test_rfid_services_version_check_unsupported(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test RFID services are properly gated behind minimum firmware versions."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry = entity_registry.async_get("sensor.openevse_station_status")
    assert entry
    assert entry.device_id

    manager = hass.data[DOMAIN][entry.config_entry_id][MANAGER]

    # Test when version_check returns False
    with (
        patch.object(
            manager,
            "version_check",
            return_value=False,
        ),
        caplog.at_level(logging.WARNING),
    ):
        # 1. add_rfid_tag (requires 4.0.0+)
        await hass.services.async_call(
            DOMAIN,
            SERVICE_ADD_RFID_TAG,
            {ATTR_DEVICE_ID: entry.device_id},
            blocking=True,
        )
        assert (
            "RFID tag learning requires firmware version 4.0.0 or higher."
            in caplog.text
        )

        caplog.clear()
        # 2. set_rfid_user (requires 5.0.0+)
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_RFID_USER,
            {
                ATTR_DEVICE_ID: entry.device_id,
                ATTR_RFID: "01020304",
                ATTR_NAME: "Alice",
            },
            blocking=True,
        )
        assert (
            "Managing RFID users requires firmware version 5.0.0 or higher."
            in caplog.text
        )

        caplog.clear()
        # 3. delete_rfid_user (requires 5.0.0+)
        await hass.services.async_call(
            DOMAIN,
            SERVICE_DELETE_RFID_USER,
            {
                ATTR_DEVICE_ID: entry.device_id,
                ATTR_RFID: "01020304",
            },
            blocking=True,
        )
        assert (
            "Managing RFID users requires firmware version 5.0.0 or higher."
            in caplog.text
        )

        caplog.clear()
        # 4. get_rfid_users (requires 5.0.0+)
        response = await hass.services.async_call(
            DOMAIN,
            SERVICE_GET_RFID_USERS,
            {ATTR_DEVICE_ID: entry.device_id},
            blocking=True,
            return_response=True,
        )
        assert response == {}
        assert (
            "Managing RFID users requires firmware version 5.0.0 or higher."
            in caplog.text
        )


async def test_service_invalid_device_id(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
):
    """Test all services with an invalid device ID."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(TEST_URL_OVERRIDE, status=200, text="{}")

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    services_to_test = [
        (SERVICE_SET_OVERRIDE, {}),
        (SERVICE_CLEAR_OVERRIDE, {}),
        (SERVICE_SET_LIMIT, {ATTR_TYPE: "time", ATTR_VALUE: 60}),
        (SERVICE_CLEAR_LIMIT, {}),
        (SERVICE_GET_LIMIT, {}),
        (SERVICE_MAKE_CLAIM, {}),
        (SERVICE_RELEASE_CLAIM, {}),
        (SERVICE_LIST_CLAIMS, {}),
        (SERVICE_LIST_OVERRIDES, {}),
        (SERVICE_GET_TIME, {}),
        (SERVICE_SET_TIME, {ATTR_SNTP: True}),
        (SERVICE_SYNC_TIME, {}),
        (SERVICE_ADD_RFID_TAG, {}),
        (SERVICE_SET_RFID_USER, {ATTR_RFID: "01020304", ATTR_NAME: "Alice"}),
        (SERVICE_GET_RFID_USERS, {}),
        (SERVICE_GET_CERTIFICATES, {}),
        (SERVICE_ADD_CERTIFICATE, {ATTR_NAME: "test", ATTR_CERTIFICATE: "test"}),
        (SERVICE_DELETE_CERTIFICATE, {ATTR_CERTIFICATE_ID: "3a8f"}),
        (SERVICE_GET_NOTIFICATIONS, {}),
        (SERVICE_ACK_NOTIFICATION, {ATTR_NOTIFICATION_ID: "safety.ground_check"}),
        (SERVICE_RESET_ENERGY_METER, {}),
    ]

    for service_name, data in services_to_test:
        payload = {ATTR_DEVICE_ID: "fake_device_id"}
        payload.update(data)

        # Determine if return_response is needed
        return_response = service_name in [
            SERVICE_GET_LIMIT,
            SERVICE_LIST_CLAIMS,
            SERVICE_LIST_OVERRIDES,
            SERVICE_GET_TIME,
            SERVICE_GET_RFID_USERS,
            SERVICE_GET_CERTIFICATES,
            SERVICE_GET_NOTIFICATIONS,
        ]

        with pytest.raises(ValueError, match="Device ID fake_device_id is not valid"):
            await hass.services.async_call(
                DOMAIN,
                service_name,
                payload,
                blocking=True,
                return_response=return_response,
            )


async def test_service_missing_config(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test all services where config/manager is missing."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(TEST_URL_OVERRIDE, status=200, text="{}")

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry_entity = entity_registry.async_get("sensor.openevse_station_status")

    hass.data[DOMAIN] = {}

    services_to_test = [
        (SERVICE_SET_OVERRIDE, {}),
        (SERVICE_CLEAR_OVERRIDE, {}),
        (SERVICE_SET_LIMIT, {ATTR_TYPE: "time", ATTR_VALUE: 60}),
        (SERVICE_CLEAR_LIMIT, {}),
        (SERVICE_GET_LIMIT, {}),
        (SERVICE_MAKE_CLAIM, {}),
        (SERVICE_RELEASE_CLAIM, {}),
        (SERVICE_LIST_CLAIMS, {}),
        (SERVICE_LIST_OVERRIDES, {}),
        (SERVICE_GET_TIME, {}),
        (SERVICE_SET_TIME, {ATTR_SNTP: True}),
        (SERVICE_SYNC_TIME, {}),
        (SERVICE_ADD_RFID_TAG, {}),
        (SERVICE_SET_RFID_USER, {ATTR_RFID: "01020304", ATTR_NAME: "Alice"}),
        (SERVICE_DELETE_RFID_USER, {ATTR_RFID: "01020304"}),
        (SERVICE_GET_RFID_USERS, {}),
        (SERVICE_GET_CERTIFICATES, {}),
        (SERVICE_ADD_CERTIFICATE, {ATTR_NAME: "test", ATTR_CERTIFICATE: "test"}),
        (SERVICE_DELETE_CERTIFICATE, {ATTR_CERTIFICATE_ID: "3a8f"}),
        (SERVICE_GET_NOTIFICATIONS, {}),
        (SERVICE_ACK_NOTIFICATION, {ATTR_NOTIFICATION_ID: "safety.ground_check"}),
        (SERVICE_RESET_ENERGY_METER, {}),
    ]

    for service_name, data in services_to_test:
        payload = {ATTR_DEVICE_ID: entry_entity.device_id}
        payload.update(data)

        # Determine if return_response is needed
        return_response = service_name in [
            SERVICE_GET_LIMIT,
            SERVICE_LIST_CLAIMS,
            SERVICE_LIST_OVERRIDES,
            SERVICE_GET_TIME,
            SERVICE_GET_RFID_USERS,
            SERVICE_GET_CERTIFICATES,
            SERVICE_GET_NOTIFICATIONS,
        ]

        caplog.clear()

        with caplog.at_level(logging.ERROR):
            await hass.services.async_call(
                DOMAIN,
                service_name,
                payload,
                blocking=True,
                return_response=return_response,
            )
            assert "Error locating configuration" in caplog.text


async def test_services_with_none_values(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test services with missing (None) arguments."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )

    mock_aioclient.post(
        f"{TEST_URL_CLAIMS}/20",
        status=200,
        text='[{"msg":"done"}]',
    )

    # Mock set_override endpoint
    mock_aioclient.post(
        TEST_URL_OVERRIDE,
        status=200,
        text='{"msg": "OK"}',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry_entity = entity_registry.async_get("sensor.openevse_station_status")

    # 1. Test make_claim with only device_id (other args become None)
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_MAKE_CLAIM,
            {ATTR_DEVICE_ID: entry_entity.device_id},
            blocking=True,
        )
        assert "Make claim response:" in caplog.text

    # 2. Test set_override with only device_id (other args become None)
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_OVERRIDE,
            {ATTR_DEVICE_ID: entry_entity.device_id},
            blocking=True,
        )
        assert "Set Override response:" in caplog.text


async def test_services_coverage_gaps(
    hass, test_charger, mock_ws_start, entity_registry: er.EntityRegistry, caplog
):
    """Verify services coverage gaps."""
    entry = MockConfigEntry(domain=DOMAIN, data=CONFIG_DATA)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry_entity = entity_registry.async_get("sensor.openevse_station_status")

    # Test ValueError if device ID is not valid
    with pytest.raises(ValueError, match="Device ID invalid_device is not valid"):
        await hass.services.async_call(
            DOMAIN,
            "make_claim",
            {"device_id": "invalid_device", "state": "active"},
            blocking=True,
        )

    # Test ValueError if device has no connections
    dev_reg = dr.async_get(hass)
    device_no_conn = dev_reg.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, "no_conn")},
    )

    with (
        patch(
            "homeassistant.helpers.device_registry.DeviceRegistry.async_get",
            return_value=MagicMock(connections=set()),
        ),
        pytest.raises(ValueError, match="has no connections"),
    ):
        await hass.services.async_call(
            DOMAIN,
            "make_claim",
            {"device_id": device_no_conn.id, "state": "active"},
            blocking=True,
        )

    # Test services with response when no target devices are resolved
    with patch(
        "custom_components.openevse.services.OpenEVSEServices._resolve_target_device_ids",
        return_value=[],
    ):
        res_get = await hass.services.async_call(
            DOMAIN,
            SERVICE_GET_CERTIFICATES,
            {"device_id": entry_entity.device_id},
            blocking=True,
            return_response=True,
        )
        assert res_get == {}

        res_add = await hass.services.async_call(
            DOMAIN,
            SERVICE_ADD_CERTIFICATE,
            {
                "device_id": entry_entity.device_id,
                ATTR_NAME: "test",
                ATTR_CERTIFICATE: "test",
            },
            blocking=True,
            return_response=True,
        )
        assert res_add == {}


async def test_services_connection_errors(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test connection errors in all services."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(TEST_URL_OVERRIDE, status=200, text="{}")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry_entity = entity_registry.async_get("sensor.openevse_station_status")
    manager = hass.data[DOMAIN][entry.entry_id][MANAGER]

    services_to_test = [
        (SERVICE_SET_OVERRIDE, {ATTR_STATE: "active"}, "set_override"),
        (SERVICE_CLEAR_OVERRIDE, {}, "clear_override"),
        (SERVICE_SET_LIMIT, {ATTR_TYPE: "time", ATTR_VALUE: 60}, "set_limit"),
        (SERVICE_CLEAR_LIMIT, {}, "clear_limit"),
        (SERVICE_GET_LIMIT, {}, "get_limit"),
        (SERVICE_MAKE_CLAIM, {ATTR_STATE: "active"}, "make_claim"),
        (SERVICE_RELEASE_CLAIM, {}, "release_claim"),
        (SERVICE_LIST_CLAIMS, {}, "list_claims"),
        (SERVICE_LIST_OVERRIDES, {}, "get_override"),
        (SERVICE_GET_TIME, {}, "get_time"),
        (SERVICE_SET_TIME, {ATTR_SNTP: True}, "set_time"),
        (SERVICE_SYNC_TIME, {}, "sync_time"),
        (SERVICE_ADD_RFID_TAG, {}, "add_rfid_tag"),
        (
            SERVICE_SET_RFID_USER,
            {ATTR_RFID: "01020304", ATTR_NAME: "Alice"},
            "set_rfid_user",
        ),
        (
            SERVICE_DELETE_RFID_USER,
            {ATTR_RFID: "01020304"},
            "delete_rfid_user",
        ),
        (SERVICE_GET_RFID_USERS, {}, "get_rfid_users"),
        (SERVICE_GET_CERTIFICATES, {}, "get_certificates"),
        (
            SERVICE_ADD_CERTIFICATE,
            {ATTR_NAME: "test", ATTR_CERTIFICATE: "test"},
            "add_certificate",
        ),
        (
            SERVICE_DELETE_CERTIFICATE,
            {ATTR_CERTIFICATE_ID: "3a8f"},
            "delete_certificate",
        ),
        (SERVICE_GET_NOTIFICATIONS, {}, "get_notifications"),
        (
            SERVICE_ACK_NOTIFICATION,
            {ATTR_NOTIFICATION_ID: "safety.ground_check"},
            "acknowledge_notification",
        ),
        (
            SERVICE_RESET_ENERGY_METER,
            {},
            "reset_energy_meter",
        ),
    ]

    for service_name, data, manager_method in services_to_test:
        payload = {ATTR_DEVICE_ID: entry_entity.device_id}
        payload.update(data)

        # Mock the manager method to raise TimeoutError
        with patch.object(manager, manager_method, side_effect=asyncio.TimeoutError):
            caplog.clear()
            return_response = service_name in [
                SERVICE_GET_LIMIT,
                SERVICE_LIST_CLAIMS,
                SERVICE_LIST_OVERRIDES,
                SERVICE_GET_TIME,
                SERVICE_GET_RFID_USERS,
                SERVICE_GET_CERTIFICATES,
                SERVICE_GET_NOTIFICATIONS,
            ]

            result = await hass.services.async_call(
                DOMAIN,
                service_name,
                payload,
                blocking=True,
                return_response=return_response,
            )
            assert "Error connecting to device" in caplog.text
            if return_response:
                assert result == {}


async def test_services_with_entity_id(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test calling services targeting entity_id."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.post(
        TEST_URL_OVERRIDE,
        status=200,
        text='{"msg": "OK"}',
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )
    mock_aioclient.delete(
        TEST_URL_OVERRIDE,
        status=200,
        text='{"msg": "OK"}',
    )
    mock_aioclient.post(
        TEST_URL_LIMIT,
        status=200,
        text='{"msg": "OK"}',
    )
    mock_aioclient.get(
        TEST_URL_LIMIT,
        status=200,
        text='{"type": "energy", "value": 10}',
    )
    mock_aioclient.delete(
        TEST_URL_LIMIT,
        status=200,
        text='{"msg": "Deleted"}',
    )
    mock_aioclient.post(
        f"{TEST_URL_CLAIMS}/20",
        status=200,
        text='[{"msg":"done"}]',
    )
    mock_aioclient.delete(
        f"{TEST_URL_CLAIMS}/20",
        status=200,
        text='[{"msg":"done"}]',
    )
    mock_aioclient.get(
        TEST_URL_CLAIMS,
        status=200,
        text='[{"client": 4, "priority": 500, "state": "disabled", "auto_release": true}]',  # noqa: E501
    )
    mock_aioclient.get(
        TEST_URL_TIME,
        status=200,
        text='{"time": "2026-03-25T15:30:00Z", "timezone": "UTC", "sntp": true}',
    )
    mock_aioclient.post(
        TEST_URL_TIME,
        status=200,
        text='{"msg": "OK"}',
    )
    mock_aioclient.post(
        TEST_URL_RFID_ADD,
        status=200,
        text='{"msg": "OK"}',
    )
    mock_aioclient.post(
        TEST_URL_RFID_USERS,
        status=200,
        text='{"msg": "OK"}',
    )
    mock_aioclient.delete(
        f"{TEST_URL_RFID_USERS}?rfid=01020304",
        status=200,
        text='{"msg": "OK"}',
    )
    mock_aioclient.get(
        TEST_URL_CERTIFICATES,
        status=200,
        text='[{"id": "3a8f", "name": "Test Cert"}]',
    )
    mock_aioclient.post(
        TEST_URL_CERTIFICATES,
        status=200,
        text='{"msg": "OK", "id": "3a8f"}',
    )
    mock_aioclient.delete(
        f"{TEST_URL_CERTIFICATES}/3a8f",
        status=200,
        text='{"msg": "OK"}',
    )
    mock_aioclient.get(
        TEST_URL_RFID_USERS,
        status=200,
        text='{"01020304": "Alice"}',
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    target_entity = "sensor.openevse_charging_status"
    assert entity_registry.async_get(target_entity)

    # 1. Set override via entity_id
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_OVERRIDE,
            {
                "entity_id": target_entity,
                ATTR_STATE: "active",
                ATTR_CHARGE_CURRENT: 24,
                ATTR_AUTO_RELEASE: True,
            },
            blocking=True,
        )
        assert "Set Override response:" in caplog.text

    # 2. Clear override via entity_id
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_CLEAR_OVERRIDE,
            {"entity_id": target_entity},
            blocking=True,
        )
        assert "Override clear command sent." in caplog.text

    # 3. Set limit via entity_id
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_LIMIT,
            {
                "entity_id": target_entity,
                ATTR_TYPE: "soc",
                ATTR_VALUE: 80,
                ATTR_AUTO_RELEASE: True,
            },
            blocking=True,
        )
        assert "Set Limit response:" in caplog.text

    # 4. Clear limit via entity_id
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_CLEAR_LIMIT,
            {"entity_id": target_entity},
            blocking=True,
        )
        assert "Limit clear command sent." in caplog.text

    # 5. Get limit via entity_id
    response = await hass.services.async_call(
        DOMAIN,
        SERVICE_GET_LIMIT,
        {"entity_id": target_entity},
        blocking=True,
        return_response=True,
    )
    assert response == {"type": "energy", "value": 10}

    # 6. Make claim via entity_id
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_MAKE_CLAIM,
            {
                "entity_id": target_entity,
                ATTR_STATE: "active",
            },
            blocking=True,
        )
        assert "Make claim response:" in caplog.text

    # 7. Release claim via entity_id
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_RELEASE_CLAIM,
            {"entity_id": target_entity},
            blocking=True,
        )
        assert "Release claim command sent." in caplog.text

    # 8. List claims via entity_id
    response = await hass.services.async_call(
        DOMAIN,
        SERVICE_LIST_CLAIMS,
        {"entity_id": target_entity},
        blocking=True,
        return_response=True,
    )
    assert response == {
        0: {
            "client": 4,
            "priority": 500,
            "state": "disabled",
            "auto_release": True,
        }
    }

    # 9. List overrides via entity_id
    response = await hass.services.async_call(
        DOMAIN,
        SERVICE_LIST_OVERRIDES,
        {"entity_id": target_entity},
        blocking=True,
        return_response=True,
    )
    assert response == {}

    # 10. Get time via entity_id
    response = await hass.services.async_call(
        DOMAIN,
        SERVICE_GET_TIME,
        {"entity_id": target_entity},
        blocking=True,
        return_response=True,
    )
    assert response == {
        "time": "2026-03-25T15:30:00Z",
        "timezone": "UTC",
        "sntp": True,
    }

    # 11. Set time via entity_id
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_TIME,
            {
                "entity_id": target_entity,
                ATTR_TIME: "2026-03-25T15:30:00Z",
                ATTR_TIMEZONE: "UTC",
                ATTR_SNTP: True,
            },
            blocking=True,
        )
        assert "Set time command sent successfully." in caplog.text

    # 12. Sync time via entity_id
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SYNC_TIME,
            {"entity_id": target_entity},
            blocking=True,
        )
        assert "Sync time command sent successfully." in caplog.text

    # 13. Add RFID tag via entity_id
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_ADD_RFID_TAG,
            {"entity_id": target_entity},
            blocking=True,
        )
        assert "Add RFID tag command sent successfully." in caplog.text

    # 14. Set RFID user via entity_id
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_RFID_USER,
            {
                "entity_id": target_entity,
                ATTR_RFID: "01020304",
                ATTR_NAME: "Alice",
            },
            blocking=True,
        )
        assert "Set RFID user command sent successfully." in caplog.text

    # 15. Delete RFID user via entity_id
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_DELETE_RFID_USER,
            {
                "entity_id": target_entity,
                ATTR_RFID: "01020304",
            },
            blocking=True,
        )
        assert "Delete RFID user command sent successfully." in caplog.text

    # 16. Get RFID users via entity_id
    response = await hass.services.async_call(
        DOMAIN,
        SERVICE_GET_RFID_USERS,
        {"entity_id": target_entity},
        blocking=True,
        return_response=True,
    )
    assert response == {"users": {"01020304": "Alice"}}

    # 17. Get certificates via entity_id
    response = await hass.services.async_call(
        DOMAIN,
        SERVICE_GET_CERTIFICATES,
        {"entity_id": target_entity},
        blocking=True,
        return_response=True,
    )
    assert response == {"certificates": [{"id": "3a8f", "name": "Test Cert"}]}

    # 18. Add certificate via entity_id
    response = await hass.services.async_call(
        DOMAIN,
        SERVICE_ADD_CERTIFICATE,
        {
            "entity_id": target_entity,
            ATTR_NAME: "Test Cert",
            ATTR_CERTIFICATE: (
                "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"
            ),
            ATTR_KEY: "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----",
        },
        blocking=True,
        return_response=True,
    )
    assert response == {"msg": "OK", "id": "3a8f"}

    # 19. Delete certificate via entity_id
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_DELETE_CERTIFICATE,
            {
                "entity_id": target_entity,
                ATTR_CERTIFICATE_ID: "3a8f",
            },
            blocking=True,
        )
        assert "Delete certificate command sent successfully." in caplog.text


async def test_service_invalid_entity_id(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
):
    """Test services with an invalid entity ID."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(TEST_URL_OVERRIDE, status=200, text="{}")

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(ValueError, match="Entity ID sensor.nonexistent is not valid"):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_OVERRIDE,
            {"entity_id": "sensor.nonexistent", ATTR_STATE: "active"},
            blocking=True,
        )


async def test_service_entity_without_device_id(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
):
    """Test services with an entity ID that has no associated device ID."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(TEST_URL_OVERRIDE, status=200, text="{}")

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Create a dummy entity with no device_id
    entity_registry.async_get_or_create(
        domain="sensor",
        platform="openevse",
        unique_id="no_device_entity",
        suggested_object_id="no_device_entity",
        device_id=None,
    )

    # Calling service should gracefully do nothing because no device_id is found
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_OVERRIDE,
        {"entity_id": "sensor.no_device_entity", ATTR_STATE: "active"},
        blocking=True,
    )

    # Calling services that return responses with no device resolved returns {}
    for service_name in [
        SERVICE_GET_LIMIT,
        SERVICE_LIST_CLAIMS,
        SERVICE_LIST_OVERRIDES,
        SERVICE_GET_TIME,
        SERVICE_GET_RFID_USERS,
        SERVICE_GET_CERTIFICATES,
        SERVICE_GET_NOTIFICATIONS,
    ]:
        res = await hass.services.async_call(
            DOMAIN,
            service_name,
            {"entity_id": "sensor.no_device_entity"},
            blocking=True,
            return_response=True,
        )
        assert res == {}


async def test_certificate_services(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test certificate services with success, specific id, and failures."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )
    mock_aioclient.get(
        TEST_URL_CERTIFICATES,
        status=200,
        text='[{"id": "3a8f", "name": "CA Root"}]',
    )
    mock_aioclient.get(
        f"{TEST_URL_CERTIFICATES}/3a8f",
        status=200,
        text='{"id": "3a8f", "name": "CA Root", "type": "ca"}',
    )
    mock_aioclient.post(
        TEST_URL_CERTIFICATES,
        status=200,
        text='{"msg": "OK", "id": "4b9c"}',
    )
    mock_aioclient.delete(
        f"{TEST_URL_CERTIFICATES}/4b9c",
        status=200,
        text='{"msg": "OK"}',
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    target_entity = "sensor.openevse_charging_status"
    assert entity_registry.async_get(target_entity)

    # 1. Get all certificates
    res = await hass.services.async_call(
        DOMAIN,
        SERVICE_GET_CERTIFICATES,
        {"entity_id": target_entity},
        blocking=True,
        return_response=True,
    )
    assert res == {"certificates": [{"id": "3a8f", "name": "CA Root"}]}

    # 2. Get specific certificate
    res = await hass.services.async_call(
        DOMAIN,
        SERVICE_GET_CERTIFICATES,
        {"entity_id": target_entity, ATTR_CERTIFICATE_ID: "3a8f"},
        blocking=True,
        return_response=True,
    )
    assert res == {"certificates": {"id": "3a8f", "name": "CA Root", "type": "ca"}}

    # 3. Add certificate
    res = await hass.services.async_call(
        DOMAIN,
        SERVICE_ADD_CERTIFICATE,
        {
            "entity_id": target_entity,
            ATTR_NAME: "Client Cert",
            ATTR_CERTIFICATE: (
                "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"
            ),
            ATTR_KEY: "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----",
        },
        blocking=True,
        return_response=True,
    )
    assert res == {"msg": "OK", "id": "4b9c"}

    # 4. Delete certificate
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_DELETE_CERTIFICATE,
            {"entity_id": target_entity, ATTR_CERTIFICATE_ID: "4b9c"},
            blocking=True,
        )
        assert "Delete certificate command sent successfully." in caplog.text


async def test_certificate_services_firmware_check(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test certificate services when firmware version is below 4.0.0."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    manager = hass.data[DOMAIN][entry.entry_id][MANAGER]
    manager.version_check = MagicMock(return_value=False)

    target_entity = "sensor.openevse_charging_status"

    with caplog.at_level(logging.WARNING):
        res = await hass.services.async_call(
            DOMAIN,
            SERVICE_GET_CERTIFICATES,
            {"entity_id": target_entity},
            blocking=True,
            return_response=True,
        )
        assert res == {}
        assert (
            "Managing certificates requires firmware version 4.0.0 or higher."
            in caplog.text
        )

    caplog.clear()
    with caplog.at_level(logging.WARNING):
        res = await hass.services.async_call(
            DOMAIN,
            SERVICE_ADD_CERTIFICATE,
            {
                "entity_id": target_entity,
                ATTR_NAME: "Test",
                ATTR_CERTIFICATE: "test-cert",
            },
            blocking=True,
            return_response=True,
        )
        assert res == {}
        assert (
            "Managing certificates requires firmware version 4.0.0 or higher."
            in caplog.text
        )

    caplog.clear()
    with caplog.at_level(logging.WARNING):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_DELETE_CERTIFICATE,
            {"entity_id": target_entity, ATTR_CERTIFICATE_ID: "3a8f"},
            blocking=True,
        )
        assert (
            "Managing certificates requires firmware version 4.0.0 or higher."
            in caplog.text
        )


async def test_certificate_services_command_failed(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
):
    """Test certificate services handling CommandFailedError."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    manager = hass.data[DOMAIN][entry.entry_id][MANAGER]
    manager.get_certificates = AsyncMock(
        side_effect=CommandFailedError("Corrupt certificate store")
    )
    manager.add_certificate = AsyncMock(
        side_effect=CommandFailedError("Invalid cert format")
    )
    manager.delete_certificate = AsyncMock(
        side_effect=CommandFailedError("Certificate not found")
    )

    target_entity = "sensor.openevse_charging_status"

    with pytest.raises(HomeAssistantError, match="Error retrieving certificates"):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_GET_CERTIFICATES,
            {"entity_id": target_entity},
            blocking=True,
            return_response=True,
        )

    with pytest.raises(HomeAssistantError, match="Error adding certificate"):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_ADD_CERTIFICATE,
            {
                "entity_id": target_entity,
                ATTR_NAME: "Test",
                ATTR_CERTIFICATE: "bad-cert",
            },
            blocking=True,
        )

    with pytest.raises(HomeAssistantError, match="Error deleting certificate"):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_DELETE_CERTIFICATE,
            {"entity_id": target_entity, ATTR_CERTIFICATE_ID: "bad_id"},
            blocking=True,
        )


async def test_notification_services(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test get_notifications and acknowledge_notification services."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )
    notif_data = {
        "count": 1,
        "max_severity": "warning",
        "notifications": [
            {
                "id": "safety.ground_check",
                "category": "safety",
                "severity": "warning",
                "sticky": False,
                "acked": False,
                "first_seen": 1726050000,
                "last_seen": 1726050005,
            }
        ],
    }
    mock_aioclient.get(
        TEST_URL_NOTIFICATIONS,
        status=200,
        text=json.dumps(notif_data),
    )
    mock_aioclient.post(
        TEST_URL_NOTIFICATIONS_ACK,
        status=200,
        text='{"msg": "OK"}',
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    target_entity = "sensor.openevse_charging_status"
    assert entity_registry.async_get(target_entity)

    # 1. Get notifications
    res = await hass.services.async_call(
        DOMAIN,
        SERVICE_GET_NOTIFICATIONS,
        {"entity_id": target_entity},
        blocking=True,
        return_response=True,
    )
    assert res == notif_data

    # 2. Acknowledge notification
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_ACK_NOTIFICATION,
            {
                "entity_id": target_entity,
                ATTR_NOTIFICATION_ID: "safety.ground_check",
            },
            blocking=True,
        )
        assert (
            "Notification safety.ground_check acknowledged successfully." in caplog.text
        )


async def test_notification_services_firmware_check(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test notification services when firmware version is below 5.1.0."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    manager = hass.data[DOMAIN][entry.entry_id][MANAGER]
    manager.version_check = MagicMock(return_value=False)

    target_entity = "sensor.openevse_charging_status"

    with caplog.at_level(logging.WARNING):
        res = await hass.services.async_call(
            DOMAIN,
            SERVICE_GET_NOTIFICATIONS,
            {"entity_id": target_entity},
            blocking=True,
            return_response=True,
        )
        assert res == {}
        assert (
            "Retrieving advisory notifications requires firmware version"
            " 5.1.0 or higher." in caplog.text
        )

    caplog.clear()
    with caplog.at_level(logging.WARNING):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_ACK_NOTIFICATION,
            {
                "entity_id": target_entity,
                ATTR_NOTIFICATION_ID: "safety.ground_check",
            },
            blocking=True,
        )
        assert (
            "Acknowledging notification requires firmware version 5.1.0 or higher."
            in caplog.text
        )


async def test_notification_services_command_failed(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
):
    """Test notification services handling CommandFailedError."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    manager = hass.data[DOMAIN][entry.entry_id][MANAGER]
    manager.get_notifications = AsyncMock(
        side_effect=CommandFailedError("Corrupt notifications endpoint")
    )
    manager.acknowledge_notification = AsyncMock(
        side_effect=CommandFailedError("Failed to ack")
    )

    target_entity = "sensor.openevse_charging_status"

    with pytest.raises(HomeAssistantError, match="Error retrieving notifications"):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_GET_NOTIFICATIONS,
            {"entity_id": target_entity},
            blocking=True,
            return_response=True,
        )

    with pytest.raises(HomeAssistantError, match="Error acknowledging notification"):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_ACK_NOTIFICATION,
            {
                "entity_id": target_entity,
                ATTR_NOTIFICATION_ID: "safety.ground_check",
            },
            blocking=True,
        )


async def test_reset_energy_meter_service(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test reset_energy_meter service calls."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    manager = hass.data[DOMAIN][entry.entry_id][MANAGER]
    manager.reset_energy_meter = AsyncMock()

    target_entity = "sensor.openevse_charging_status"
    assert entity_registry.async_get(target_entity)

    # 1. Reset energy meter with default arguments (hard=False, import=False)
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_RESET_ENERGY_METER,
            {"entity_id": target_entity},
            blocking=True,
        )
        assert (
            "Energy meter reset successfully (hard=False, import=False)." in caplog.text
        )
    manager.reset_energy_meter.assert_awaited_once_with(
        hard=False, import_from_evse=False
    )

    # 2. Reset energy meter with hard=True and import=True
    manager.reset_energy_meter.reset_mock()
    caplog.clear()
    with caplog.at_level(logging.DEBUG):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_RESET_ENERGY_METER,
            {
                "entity_id": target_entity,
                ATTR_HARD: True,
                ATTR_IMPORT: True,
            },
            blocking=True,
        )
        assert (
            "Energy meter reset successfully (hard=True, import=True)." in caplog.text
        )
    manager.reset_energy_meter.assert_awaited_once_with(
        hard=True, import_from_evse=True
    )


async def test_reset_energy_meter_firmware_check(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test reset_energy_meter when firmware version is below 4.0.0."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    manager = hass.data[DOMAIN][entry.entry_id][MANAGER]
    manager.version_check = MagicMock(return_value=False)
    manager.reset_energy_meter = AsyncMock()

    target_entity = "sensor.openevse_charging_status"

    with caplog.at_level(logging.WARNING):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_RESET_ENERGY_METER,
            {"entity_id": target_entity},
            blocking=True,
        )
        assert (
            "Resetting energy meter requires firmware version 4.0.0 or higher."
            in caplog.text
        )
    assert not manager.reset_energy_meter.called


async def test_reset_energy_meter_command_failed(
    hass,
    test_charger_services,
    mock_aioclient,
    mock_ws_start,
    entity_registry: er.EntityRegistry,
):
    """Test reset_energy_meter handling CommandFailedError."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    mock_aioclient.get(
        TEST_URL_OVERRIDE,
        status=200,
        text="{}",
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    manager = hass.data[DOMAIN][entry.entry_id][MANAGER]
    manager.reset_energy_meter = AsyncMock(
        side_effect=CommandFailedError("Reset failed")
    )

    target_entity = "sensor.openevse_charging_status"

    with pytest.raises(HomeAssistantError, match="Error resetting energy meter"):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_RESET_ENERGY_METER,
            {"entity_id": target_entity},
            blocking=True,
        )
