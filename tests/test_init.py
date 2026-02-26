"""Test openevse setup process."""

from unittest import mock
from unittest.mock import patch

import pytest
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import CoreState
from homeassistant.helpers.update_coordinator import UpdateFailed
from openevsehttp.exceptions import MissingSerial
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openevse import (
    CommandFailed,
    InvalidValue,
    OpenEVSEFirmwareCheck,
    get_firmware,
    send_command,
)
from custom_components.openevse.const import COORDINATOR, DOMAIN

from .const import (
    CONFIG_DATA,
    CONFIG_DATA_GRID,
    CONFIG_DATA_SOLAR,
    OPTIONS_DATA_GRID,
    OPTIONS_DATA_SHAPER,
    OPTIONS_DATA_SOLAR,
)

pytestmark = pytest.mark.asyncio

CHARGER_NAME = "openevse"


async def test_setup_entry(hass, test_charger, mock_ws_start):
    """Test setup_entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
        version=2,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 23
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
        version=2,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 23
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
        version=2,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 23
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
        options=OPTIONS_DATA_GRID,
        version=2,
    )
    # set a fake sensor for grid usage
    hass.states.async_set(grid_entity, "4100")
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
        options=OPTIONS_DATA_GRID,
        version=2,
    )
    # set a fake sensor for grid usage
    hass.states.async_set(grid_entity, "4100")
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
        options=OPTIONS_DATA_SOLAR,
        version=2,
    )
    # set a fake sensor for grid usage
    hass.states.async_set(solar_entity, "100")
    hass.states.async_set(voltage_entity, "110")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 25
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
        options=OPTIONS_DATA_SOLAR,
        version=2,
    )
    # set a fake sensor for grid usage
    hass.states.async_set(solar_entity, "100")
    hass.states.async_set(voltage_entity, "110")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 25
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
        version=2,
    )

    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(BINARY_SENSOR_DOMAIN)) == 4
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 23
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
        version=2,
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
        options=OPTIONS_DATA_GRID,
        version=2,
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
        version=2,
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    # Replace the manager's websocket object with a Mock.
    # This allows us to set the 'state' attribute freely without AttributeError.
    with (
        patch.object(coordinator._manager, "websocket") as mock_ws,
        patch.object(coordinator._manager, "ws_start") as mock_ws_connect,
    ):
        # Set the state on the mock websocket to 'disconnected'
        mock_ws.state = "disconnected"

        # Trigger a manual refresh which checks the websocket state
        await coordinator.async_refresh()
        await hass.async_block_till_done()

        # Verify ws_start was called to reconnect
        assert mock_ws_connect.called


async def test_send_command_utility(hass):
    """Test the send_command utility function directly."""
    mock_handler = mock.AsyncMock()

    # 1. Success case
    # Returns (command_sent, response)
    mock_handler.send_command.return_value = ("$CMD", "$OK")
    await send_command(mock_handler, "$CMD")

    # 2. Invalid Value case ($NK^21 response)
    mock_handler.send_command.return_value = ("$CMD", "$NK^21")
    with pytest.raises(InvalidValue):
        await send_command(mock_handler, "$CMD")

    # 3. Command Failed case (Response command mismatch)
    mock_handler.send_command.return_value = ("$OTHER", "$OK")
    with pytest.raises(CommandFailed):
        await send_command(mock_handler, "$CMD")


async def test_coordinator_update_errors(hass, test_charger, mock_ws_start):
    """Test error handling during coordinator updates."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
        version=2,
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    # 1. RuntimeError during manager.update() should be swallowed (logged)
    with patch.object(
        coordinator._manager, "update", side_effect=RuntimeError("Ignored")
    ):
        await coordinator._async_update_data()

    # 2. Generic Exception during manager.update() should raise UpdateFailed
    with patch.object(
        coordinator._manager, "update", side_effect=Exception("Critical")
    ):
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()


async def test_coordinator_websocket_connect_errors(hass, test_charger, mock_ws_start):
    """Test error handling during websocket connection in coordinator."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
        version=2,
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    # Force websocket state to disconnected to trigger connection logic
    with patch.object(coordinator._manager, "websocket") as mock_ws:
        mock_ws.state = "disconnected"

        # 1. RuntimeError during ws_start() should be swallowed
        with patch.object(
            coordinator._manager, "ws_start", side_effect=RuntimeError("Ignored")
        ):
            await coordinator._async_update_data()

        # 2. Generic Exception during ws_start() should raise UpdateFailed
        with patch.object(
            coordinator._manager, "ws_start", side_effect=Exception("Critical")
        ):
            with pytest.raises(UpdateFailed):
                await coordinator._async_update_data()


async def test_get_firmware_logic(hass):
    """Test get_firmware edge cases."""
    mock_manager = mock.AsyncMock()

    # 1. Update failed
    mock_manager.update.side_effect = Exception("Connection Error")
    res = await get_firmware(mock_manager)
    assert res == ("", "")

    # 2. Missing Serial (should return fallback versions)
    mock_manager.update.side_effect = None  # Reset
    mock_manager.test_and_get.side_effect = MissingSerial
    mock_manager.wifi_firmware = "1.2.3"
    mock_manager.openevse_firmware = "4.5.6"

    res = await get_firmware(mock_manager)
    assert res == ("Wifi version 1.2.3", "4.5.6")


async def test_firmware_check_coordinator(hass):
    """Test the firmware check coordinator."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
        version=2,
    )
    mock_manager = mock.AsyncMock()
    mock_manager.firmware_check.return_value = {"latest": "1.0.0"}

    coordinator = OpenEVSEFirmwareCheck(hass, 3600, entry, mock_manager)

    data = await coordinator._async_update_data()
    assert data == {"latest": "1.0.0"}
    assert mock_manager.firmware_check.called


async def test_setup_entry_not_ready(hass, test_charger, mock_ws_start):
    """Test setup entry sets state to SETUP_RETRY on update failure."""
    entry = MockConfigEntry(domain=DOMAIN, data=CONFIG_DATA, version=2)

    # Mock OpenEVSE.update to raise exception (simulating connection failure)
    with patch(
        "custom_components.openevse.OpenEVSE.update",
        side_effect=Exception("Connection Error"),
    ):
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        # The exception is caught by HA, so we check the entry state instead of asserting raises
        assert entry.state == ConfigEntryState.SETUP_RETRY


async def test_coordinator_parse_errors(hass, test_charger, mock_ws_start, caplog):
    """Test parsing sensors handles missing attributes/errors without crashing."""
    entry = MockConfigEntry(domain=DOMAIN, data=CONFIG_DATA, version=2)
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    # 1. Test Sync Parse Error
    # Patch the property on the CLASS, not the instance, to avoid 'no setter' errors
    with patch(
        "custom_components.openevse.OpenEVSE.status", new_callable=mock.PropertyMock
    ) as mock_status:
        mock_status.side_effect = ValueError("Sync Parse Error")

        coordinator.parse_sensors()
        assert "Could not update status for status" in caplog.text

    # 2. Test Async Parse Error
    # Patch the property on the CLASS
    with patch(
        "custom_components.openevse.OpenEVSE.async_override_state",
        new_callable=mock.PropertyMock,
    ) as mock_async_prop:
        mock_async_prop.side_effect = ValueError("Async Parse Error")

        await coordinator.async_parse_sensors()
        assert "Could not update status for override_state" in caplog.text


async def test_websocket_update_callback(hass, test_charger, mock_ws_start):
    """Test websocket callback triggers data update on coordinator."""
    entry = MockConfigEntry(domain=DOMAIN, data=CONFIG_DATA, version=2)
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    # Mock async_set_updated_data to verify it is called
    with patch.object(coordinator, "async_set_updated_data") as mock_update:
        await coordinator.websocket_update()
        assert mock_update.called


async def test_setup_entry_when_ha_running(hass, test_charger, mock_ws_start):
    """Test setup when HA is already running registers listeners immediately."""
    # Simulate HA being fully started
    hass.state = CoreState.running

    # Use config with grid/solar sensors to ensure listeners are registered
    entry = MockConfigEntry(
        domain=DOMAIN, data=CONFIG_DATA_GRID, options=OPTIONS_DATA_GRID, version=2
    )

    with patch(
        "custom_components.openevse.async_track_state_change_event"
    ) as mock_track:
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        # Verify listeners were tracked immediately
        assert mock_track.called


async def test_setup_entry_state_change_shaper(
    hass, test_charger, mock_ws_start, caplog
):
    """Test state change with shaper sensor."""
    shaper_entity = "sensor.shaper_power"
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
        options=OPTIONS_DATA_SHAPER,
        version=2,
    )
    # set a fake sensor for shaper power
    hass.states.async_set(shaper_entity, "2500")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1
    await hass.async_block_till_done()

    hass.states.async_set(shaper_entity, "3000")
    await hass.async_block_till_done()

    assert "Sending sensor data to OpenEVSE: (shaper: 3000)" in caplog.text


async def test_setup_entry_state_change_shaper_timeout(
    hass, test_charger, mock_ws_start, caplog
):
    """Test state change with shaper sensor timeout."""
    shaper_entity = "sensor.shaper_power"
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
        options=OPTIONS_DATA_SHAPER,
        version=2,
    )
    # set a fake sensor for shaper power
    hass.states.async_set(shaper_entity, "2500")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1
    await hass.async_block_till_done()

    with patch(
        "custom_components.openevse.OpenEVSE.set_shaper_live_pwr",
        side_effect=TimeoutError,
    ):
        hass.states.async_set(shaper_entity, "3000")
        await hass.async_block_till_done()

    assert (
        "Timeout error connecting to device: , please check your network connection."
        in caplog.text
    )
