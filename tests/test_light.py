"""Provide tests for OpenEVSE light platform."""

import pytest
from homeassistant.components.light import ATTR_BRIGHTNESS
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openevse.const import DOMAIN

from .conftest import TEST_URL_CONFIG
from .const import CONFIG_DATA

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


async def test_light_v2(
    hass,
    test_charger_v2,
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

    assert len(hass.states.async_entity_ids(LIGHT_DOMAIN)) == 0
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1

    assert DOMAIN in hass.config.components
