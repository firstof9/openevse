"""Test openevse select entities."""

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


async def test_select(
    hass, test_charger, mock_ws_start, entity_registry: er.EntityRegistry, caplog
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

    assert len(hass.states.async_entity_ids(SELECT_DOMAIN)) == 3
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1

    assert DOMAIN in hass.config.components

    entity_id = "select.openevse_override_state"

    state = hass.states.get(entity_id)
    assert state
    assert state.state == "auto"
