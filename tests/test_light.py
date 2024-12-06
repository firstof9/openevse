"""Provide tests for OpenEVSE light platform."""

from datetime import timedelta
from unittest.mock import patch

import pytest
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN, ATTR_BRIGHTNESS
from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openevse.const import DOMAIN

from .const import CONFIG_DATA
from .conftest import TEST_URL_CONFIG

pytestmark = pytest.mark.asyncio

CHARGER_NAME = "openevse"


async def test_light(
    hass,
    test_charger,
    mock_ws_start,
    mock_aioclient,
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
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 21
    assert len(hass.states.async_entity_ids(SWITCH_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SELECT_DOMAIN)) == 2
    assert len(hass.states.async_entity_ids(NUMBER_DOMAIN)) == 1
    assert len(hass.states.async_entity_ids(LIGHT_DOMAIN)) == 1
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1

    assert DOMAIN in hass.config.components

    entity_id = "light.openevse_led_brightness"
    state = hass.states.get(entity_id)
    assert state
    assert state.state == "on"
    assert state.attributes[ATTR_BRIGHTNESS] == 64

    mock_aioclient.post(
        TEST_URL_CONFIG,
        status=200,
        body='{"msg": "Ok"}',
        repeat=True,
    )

    await hass.services.async_call(
        LIGHT_DOMAIN,
        "turn_off",
        {"entity_id": entity_id},
        blocking=True,
    )

    mock_aioclient.assert_any_call(
        TEST_URL_CONFIG, method="POST", data={ATTR_BRIGHTNESS: 0}
    )

    await hass.services.async_call(
        LIGHT_DOMAIN,
        "turn_on",
        {"entity_id": entity_id},
        blocking=True,
    )

    mock_aioclient.assert_any_call(
        TEST_URL_CONFIG, method="POST", data={ATTR_BRIGHTNESS: 128}
    )

    await hass.services.async_call(
        LIGHT_DOMAIN,
        "turn_on",
        {"entity_id": entity_id, "brightness": 26},
        blocking=True,
    )

    mock_aioclient.assert_any_call(
        TEST_URL_CONFIG, method="POST", data={ATTR_BRIGHTNESS: 26}
    )
