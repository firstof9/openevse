"""Test OpenEVSE update platform."""

from unittest.mock import AsyncMock

import pytest
from homeassistant.components.update import (
    ATTR_INSTALLED_VERSION,
    ATTR_LATEST_VERSION,
    ATTR_RELEASE_URL,
)
from homeassistant.components.update import DOMAIN as UPDATE_DOMAIN
from homeassistant.exceptions import HomeAssistantError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openevse.const import COORDINATOR, DOMAIN, FW_COORDINATOR
from custom_components.openevse.update import OpenEVSEUpdateEntity
from tests.typing import WebSocketGenerator

from .const import CONFIG_DATA, FW_DATA

pytestmark = pytest.mark.asyncio

CHARGER_NAME = "openevse"


async def test_update_entity(
    hass, test_charger, mock_ws_start, hass_ws_client: WebSocketGenerator
):
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
    assert state.attributes[ATTR_RELEASE_URL] == FW_DATA["release_url"]

    await ws_client.send_json(
        {
            "id": 1,
            "type": "update/release_notes",
            "entity_id": entity_id,
        }
    )
    result = await ws_client.receive_json()
    assert result["result"] == FW_DATA["release_notes"]


async def test_update_coverage_gaps(hass, test_charger, mock_ws_start):
    """Test update coverage gaps."""
    entry = MockConfigEntry(domain=DOMAIN, data=CONFIG_DATA)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    fw_coordinator = hass.data[DOMAIN][entry.entry_id][FW_COORDINATOR]

    update = OpenEVSEUpdateEntity(coordinator, fw_coordinator, entry)

    # Test installed_version when coordinator data is missing
    coordinator.data = None
    assert update.installed_version is None


async def test_update_install(hass, test_charger, mock_ws_start):
    """Test update install service."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    manager = hass.data[DOMAIN][entry.entry_id]["manager"]
    manager.update_firmware = AsyncMock()

    entity_id = "update.openevse_update"
    await hass.services.async_call(
        UPDATE_DOMAIN, "install", {"entity_id": entity_id}, blocking=True
    )

    assert manager.update_firmware.called
    manager.update_firmware.assert_called_once_with(
        firmware_url="https://github.com/OpenEVSE/ESP32_WiFi_V4.x/releases/download/4.1.7/openevse_wifi_v1.bin"
    )


async def test_update_install_no_url(hass, test_charger, mock_ws_start):
    """Test update install service with no URL."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    fw_coordinator = hass.data[DOMAIN][entry.entry_id][FW_COORDINATOR]
    fw_coordinator.data = {
        "latest_version": "4.1.8",
        "browser_download_url": None,
    }

    entity_id = "update.openevse_update"
    with pytest.raises(HomeAssistantError) as excinfo:
        await hass.services.async_call(
            UPDATE_DOMAIN, "install", {"entity_id": entity_id}, blocking=True
        )
    assert str(excinfo.value) == "No firmware download URL available to install"


async def test_update_install_failure(hass, test_charger, mock_ws_start):
    """Test update install service when update fails."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    manager = hass.data[DOMAIN][entry.entry_id]["manager"]
    manager.update_firmware = AsyncMock(side_effect=RuntimeError("Update failed"))

    entity_id = "update.openevse_update"
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            UPDATE_DOMAIN, "install", {"entity_id": entity_id}, blocking=True
        )
