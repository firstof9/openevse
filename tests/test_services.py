"""Test openevse services."""

import json
import logging

import pytest
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openevse.const import (
    ATTR_AUTO_RELEASE,
    ATTR_CHARGE_CURRENT,
    ATTR_DEVICE_ID,
    ATTR_ENERGY_LIMIT,
    ATTR_MAX_CURRENT,
    ATTR_STATE,
    ATTR_TIME_LIMIT,
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
        body='[{"client": 4, "priority": 500, "state": "disabled", "auto_release": true}, {"client": 65538, "priority": 50, "state": "active", "charge_current": 7, "auto_release": false}]',  # noqa: E501
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
        TEST_URL_LIMIT,
        status=200,
        body='{"type": "energy", "value": 10}',
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
        body='{"msg": "OK"}',
    )
    # Ensure get override is mocked to avoid errors during setup/teardown updates
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
        body='{"msg": "OK"}',
    )
    mock_aioclient.get(
        TEST_URL_LIMIT,
        status=200,
        body='{"type": "time", "value": 60, "auto_release": false}',
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
    mock_aioclient.get(TEST_URL_OVERRIDE, status=200, body="{}", repeat=True)

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
    ]

    for service_name, data in services_to_test:
        payload = {ATTR_DEVICE_ID: "fake_device_id"}
        payload.update(data)

        # Determine if return_response is needed
        return_response = service_name in [
            SERVICE_GET_LIMIT,
            SERVICE_LIST_CLAIMS,
            SERVICE_LIST_OVERRIDES,
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
    mock_aioclient.get(TEST_URL_OVERRIDE, status=200, body="{}", repeat=True)

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
    ]

    for service_name, data in services_to_test:
        payload = {ATTR_DEVICE_ID: entry_entity.device_id}
        payload.update(data)

        # Determine if return_response is needed
        return_response = service_name in [
            SERVICE_GET_LIMIT,
            SERVICE_LIST_CLAIMS,
            SERVICE_LIST_OVERRIDES,
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
        body='[{"msg":"done"}]',
        repeat=True,
    )

    # Mock set_override endpoint
    mock_aioclient.post(
        TEST_URL_OVERRIDE,
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
