"""Test OpenEVSE update platform."""

import pytest
from homeassistant.components.update import (
    ATTR_INSTALLED_VERSION,
    ATTR_LATEST_VERSION,
    ATTR_RELEASE_URL,
)
from homeassistant.components.update import DOMAIN as UPDATE_DOMAIN
from pytest_homeassistant_custom_component.common import MockConfigEntry
from tests.typing import WebSocketGenerator

from custom_components.openevse.const import DOMAIN

from .const import CONFIG_DATA, FW_DATA

pytestmark = pytest.mark.asyncio

CHARGER_NAME = "openevse"


async def test_update_entity(hass, test_charger, mock_ws_start, hass_ws_client: WebSocketGenerator):
    """Test update entity setup and attributes."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    ws_client = await hass_ws_client(hass)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(UPDATE_DOMAIN)) == 1

    entity_id = "update.openevse_update"
    state = hass.states.get(entity_id)

    assert state
    assert state.attributes[ATTR_INSTALLED_VERSION] == "v5.1.2"
    assert state.attributes[ATTR_LATEST_VERSION] == FW_DATA["latest_version"]
    assert state.attributes["release_notes"] == FW_DATA["release_notes"]
    assert state.attributes[ATTR_RELEASE_URL] == FW_DATA["release_url"]

    await ws_client.send_json(
        {
            "id": 1,
            "type": "update/release_notes",
            "entity_id": entity_id,
        }
    )
    result = await ws_client.receive_json()
    assert result["result"] is FW_DATA["release_notes"]