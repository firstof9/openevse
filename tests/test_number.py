"""Test OpenEVSE number platform."""

import logging
from unittest.mock import patch

import pytest
from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.number import SERVICE_SET_VALUE
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openevse.const import COORDINATOR, DOMAIN, MANAGER, NUMBER_TYPES
from custom_components.openevse.number import OpenEVSENumberEntity

from .const import CONFIG_DATA

pytestmark = pytest.mark.asyncio

CHARGER_NAME = "openevse"
# SERVICE_SET_VALUE = "set_value"


async def test_number(
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

    assert len(hass.states.async_entity_ids(NUMBER_DOMAIN)) == 1
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1

    assert DOMAIN in hass.config.components

    entity_id = "number.openevse_charge_rate"

    state = hass.states.get(entity_id)
    assert state
    assert state.state == "28.0"

    servicedata = {
        "entity_id": entity_id,
        "value": 21,
    }

    await hass.services.async_call(
        NUMBER_DOMAIN, SERVICE_SET_VALUE, servicedata, blocking=True
    )
    await hass.async_block_till_done()

    with caplog.at_level(logging.DEBUG):
        coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
        coordinator._data["max_current_soft"] = 21
        updated_data = coordinator._data
        coordinator.async_set_updated_data(updated_data)
        await hass.async_block_till_done()

    state = hass.states.get(entity_id)
    assert state
    assert state.state == "21.0"

    hass.states.async_set(entity_id, "30.0")

    state = hass.states.get(entity_id)
    assert state
    assert state.state == "30.0"

    with caplog.at_level(logging.DEBUG):
        coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
        coordinator._data["divert_active"] = True
        updated_data = coordinator._data
        coordinator.async_set_updated_data(updated_data)
        await hass.async_block_till_done()

        state = hass.states.get(entity_id)
        assert state
        assert state.state == "unavailable"
        assert (
            "Disabling openevse Charge Rate due to PV Divert being active."
            in caplog.text
        )


async def test_number_validation_error(hass, test_charger, mock_ws_start):
    """Test validation error for non-integer charge rate."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    manager = hass.data[DOMAIN][entry.entry_id][MANAGER]
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    entity = OpenEVSENumberEntity(
        entry, coordinator, NUMBER_TYPES["max_current_soft"], manager
    )

    with pytest.raises(ValueError, match="charge rate must be whole amps"):
        await entity.async_set_native_value(21.5)

    # Test success path
    with patch.object(
        manager, "set_current", wraps=manager.set_current
    ) as mock_set_current:
        await entity.async_set_native_value(21.0)
        mock_set_current.assert_called_with(21)
