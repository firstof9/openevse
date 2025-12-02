"""Test openevse setup process."""

from unittest.mock import patch

import pytest
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openevse.const import COORDINATOR, DOMAIN

from .const import CONFIG_DATA, CONFIG_DATA_GRID, CONFIG_DATA_SOLAR

pytestmark = pytest.mark.asyncio

CHARGER_NAME = "openevse"


async def test_setup_entry(hass, test_charger, mock_ws_start):
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
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 22
    assert len(hass.states.async_entity_ids(SWITCH_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SELECT_DOMAIN)) == 3
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1


async def test_setup_entry_bad_serial(hass, test_charger_bad_serial, mock_ws_start):
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
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 22
    assert len(hass.states.async_entity_ids(SWITCH_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SELECT_DOMAIN)) == 3
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1


async def test_setup_and_unload_entry(hass, test_charger):
    """Test unloading entities."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 22
    assert len(hass.states.async_entity_ids(SWITCH_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SELECT_DOMAIN)) == 3
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1

    assert await hass.config_entries.async_unload(entries[0].entry_id)
    await hass.async_block_till_done()
    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(DOMAIN)) == 0

    assert await hass.config_entries.async_remove(entries[0].entry_id)
    await hass.async_block_till_done()
    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 0


async def test_setup_entry_state_change(hass, test_charger, mock_ws_start, caplog):
    """Test state change with grid sensor."""
    grid_entity = "sensor.grid_usage"
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA_GRID,
    )
    # set a fake sensor for grid usage
    hass.states.async_set(grid_entity, "4100")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 23
    assert len(hass.states.async_entity_ids(SWITCH_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SELECT_DOMAIN)) == 3
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1
    await hass.async_block_till_done()

    hass.states.async_set(grid_entity, "-200")
    await hass.async_block_till_done()

    assert "Sending sensor data to OpenEVSE: (grid: -200)" in caplog.text


async def test_setup_entry_state_change_timeout(
    hass, test_charger_bad_post, mock_ws_start, caplog
):
    """Test state change with grid sensor."""
    grid_entity = "sensor.grid_usage"
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA_GRID,
    )
    # set a fake sensor for grid usage
    hass.states.async_set(grid_entity, "4100")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 23
    assert len(hass.states.async_entity_ids(SWITCH_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SELECT_DOMAIN)) == 3
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1
    await hass.async_block_till_done()

    hass.states.async_set(grid_entity, "-200")
    await hass.async_block_till_done()

    assert (
        "Timeout error connecting to device: , please check your network connection."
        in caplog.text
    )


async def test_setup_entry_state_change_2(hass, test_charger, mock_ws_start, caplog):
    """Test state change with solar sensor."""
    solar_entity = "sensor.solar_production"
    voltage_entity = "sensor.grid_voltage"
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA_SOLAR,
    )
    # set a fake sensor for grid usage
    hass.states.async_set(solar_entity, "100")
    hass.states.async_set(voltage_entity, "110")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 24
    assert len(hass.states.async_entity_ids(SWITCH_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SELECT_DOMAIN)) == 3
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1
    await hass.async_block_till_done()

    hass.states.async_set(solar_entity, "2317")
    await hass.async_block_till_done()
    assert "Sending sensor data to OpenEVSE: (solar: 2317)" in caplog.text

    hass.states.async_set(voltage_entity, "113")
    await hass.async_block_till_done()
    assert "Sending sensor data to OpenEVSE: (voltage: 113)" in caplog.text


async def test_setup_entry_state_change_2_bad_post(
    hass, test_charger_bad_post, mock_ws_start, caplog
):
    """Test state change with solar sensor."""
    solar_entity = "sensor.solar_production"
    voltage_entity = "sensor.grid_voltage"
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA_SOLAR,
    )
    # set a fake sensor for grid usage
    hass.states.async_set(solar_entity, "100")
    hass.states.async_set(voltage_entity, "110")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 24
    assert len(hass.states.async_entity_ids(SWITCH_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SELECT_DOMAIN)) == 3
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1
    await hass.async_block_till_done()

    hass.states.async_set(solar_entity, "2317")
    await hass.async_block_till_done()
    assert (
        "Timeout error connecting to device: , please check your network connection."
        in caplog.text
    )

    hass.states.async_set(voltage_entity, "113")
    await hass.async_block_till_done()
    assert (
        "Timeout error connecting to device: , please check your network connection."
        in caplog.text
    )


async def test_setup_entry_v2(hass, test_charger_v2, mock_ws_start):
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
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 22
    assert len(hass.states.async_entity_ids(SWITCH_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SELECT_DOMAIN)) == 3
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1


async def test_setup_entry_old_firmware(hass, test_charger, mock_ws_start):
    """Test setup with older firmware where services are not registered."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )

    # Patch version_check to return False (simulating firmware < 4.1.0)
    # The integration uses the 'manager' object which is an instance of OpenEVSE
    with patch("custom_components.openevse.OpenEVSE.version_check", return_value=False):
        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        # Verify that a service specific to > 4.1.0 is NOT registered
        # 'set_override' is one of the services registered in services.py
        assert not hass.services.has_service(DOMAIN, "set_override")


async def test_setup_entry_state_change_unavailable(
    hass, test_charger, mock_ws_start, caplog
):
    """Test state change with unavailable grid sensor."""
    grid_entity = "sensor.grid_usage"
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA_GRID,
    )
    # Set initial valid state
    hass.states.async_set(grid_entity, "4100")

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Change state to unavailable
    hass.states.async_set(grid_entity, "unavailable")
    await hass.async_block_till_done()

    # Verify that the integration handled it by sending None (logged as None)
    assert "Sending sensor data to OpenEVSE: (grid: None)" in caplog.text


async def test_coordinator_websocket_reconnect(hass, test_charger, mock_ws_start):
    """Test websocket reconnect logic in coordinator."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    # Replace the manager's websocket object with a Mock.
    # This allows us to set the 'state' attribute freely without AttributeError.
    with patch.object(coordinator._manager, "websocket") as mock_ws, patch.object(
        coordinator._manager, "ws_start"
    ) as mock_ws_connect:

        # Set the state on the mock websocket to 'disconnected'
        mock_ws.state = "disconnected"

        # Trigger a manual refresh which checks the websocket state
        await coordinator.async_refresh()
        await hass.async_block_till_done()

        # Verify ws_start was called to reconnect
        assert mock_ws_connect.called
