"""Test openevse sensors."""

import contextlib
import logging
from datetime import datetime
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from aiohttp import ClientError
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import UnitOfLength
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openevse.const import DOMAIN
from custom_components.openevse.sensor import OpenEVSESensor

from .const import CONFIG_DATA

pytestmark = pytest.mark.asyncio

CHARGER_NAME = "openevse"
TEST_URL_OVERRIDE = "http://openevse.test.tld/override"


async def test_sensors(
    hass,
    test_charger,
    mock_ws_start,
    mock_aioclient,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test setup_entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    with caplog.at_level(logging.DEBUG):
        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 28
        entries = hass.config_entries.async_entries(DOMAIN)
        assert len(entries) == 1

        assert DOMAIN in hass.config.components

        state = hass.states.get("sensor.openevse_wifi_firmware_version")
        assert state
        assert state.state == "v5.1.2"
        state = hass.states.get("sensor.openevse_charge_time_elapsed")
        assert state
        assert state.state == "4.1"
        state = hass.states.get("sensor.openevse_total_usage")
        assert state
        assert state.state == "64582"
        state = hass.states.get("sensor.openevse_max_current")
        assert state
        assert state.state == "48"

        state = hass.states.get("sensor.openevse_override_state")
        assert state
        assert state.state == "auto"

        state = hass.states.get("sensor.openevse_charging_status")
        assert state
        assert state.attributes.get("icon") == "mdi:sleep"

        state = hass.states.get("sensor.openevse_current_power_usage_actual")
        assert state
        assert state.state == "0"

        state = hass.states.get("sensor.openevse_charging_current")
        assert state
        assert state.state == "32.2"

        state = hass.states.get("sensor.openevse_gfci_trip_count")
        assert state
        assert state.state == "1"

        state = hass.states.get("sensor.openevse_no_ground_trip_count")
        assert state
        assert state.state == "0"

        state = hass.states.get("sensor.openevse_stuck_relay_trip_count")
        assert state
        assert state.state == "0"

        state = hass.states.get("sensor.openevse_notification_count")
        assert state
        assert state.state == "1"

        state = hass.states.get("sensor.openevse_notification_severity")
        assert state
        assert state.state == "warning"

        # enable disabled sensor
        entity_id = "sensor.openevse_vehicle_charge_completion"
        entity_entry = entity_registry.async_get(entity_id)

        assert entity_entry
        assert entity_entry.disabled
        assert entity_entry.disabled_by is er.RegistryEntryDisabler.INTEGRATION

        updated_entry = entity_registry.async_update_entity(
            entity_entry.entity_id, disabled_by=None
        )
        assert updated_entry != entity_entry
        assert updated_entry.disabled is False

        # reload the integration
        assert await hass.config_entries.async_forward_entry_unload(entry, "sensor")
        await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
        await hass.async_block_till_done()

        state = hass.states.get("sensor.openevse_vehicle_charge_completion")
        assert state
        parsed_date = dt_util.parse_datetime(state.state)
        assert isinstance(parsed_date, datetime)


async def test_sensors_v2(
    hass,
    test_charger_v2,
    mock_ws_start,
    mock_aioclient,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test setup_entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    with caplog.at_level(logging.DEBUG):
        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 28
        entries = hass.config_entries.async_entries(DOMAIN)
        assert len(entries) == 1

        assert DOMAIN in hass.config.components

        state = hass.states.get("sensor.openevse_wifi_firmware_version")
        assert state
        assert state.state == "2.9.1"
        state = hass.states.get("sensor.openevse_charge_time_elapsed")
        assert state
        assert state.state == "145.85"
        state = hass.states.get("sensor.openevse_total_usage")
        assert state
        assert state.state == "1585443"
        state = hass.states.get("sensor.openevse_max_current")
        assert state
        assert state.state == "unknown"

        state = hass.states.get("sensor.openevse_override_state")
        assert state
        assert state.state == "unavailable"

        state = hass.states.get("sensor.openevse_charging_status")
        assert state
        assert state.attributes.get("icon") == "mdi:power-plug-off"

        state = hass.states.get("sensor.openevse_override_state")
        assert state
        assert state.state == "unavailable"

        state = hass.states.get("sensor.openevse_notification_count")
        assert state
        assert state.state == "unavailable"

        state = hass.states.get("sensor.openevse_notification_severity")
        assert state
        assert state.state == "unavailable"


async def test_sensors_new(
    hass,
    test_charger_new,
    mock_ws_start,
    mock_aioclient,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test setup_entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    with caplog.at_level(logging.DEBUG):
        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 28
        entries = hass.config_entries.async_entries(DOMAIN)
        assert len(entries) == 1

        assert DOMAIN in hass.config.components

        state = hass.states.get("sensor.openevse_wifi_firmware_version")
        assert state
        assert state.state == "v5.1.2"
        state = hass.states.get("sensor.openevse_charge_time_elapsed")
        assert state
        assert state.state == "0.0"
        state = hass.states.get("sensor.openevse_total_usage")
        assert state
        assert state.state == "20127.22817"
        state = hass.states.get("sensor.openevse_max_current")
        assert state
        assert state.state == "48"

        state = hass.states.get("sensor.openevse_override_state")
        assert state
        assert state.state == "auto"

        state = hass.states.get("sensor.openevse_charging_status")
        assert state
        assert state.attributes.get("icon") == "mdi:sleep"

        state = hass.states.get("sensor.openevse_current_power_usage_actual")
        assert state
        assert state.state == "6204"

        state = hass.states.get("sensor.openevse_current_power_usage_calculated")
        assert state
        assert state.state == "6204.0"

        state = hass.states.get("sensor.openevse_charging_current")
        assert state
        assert state.state == "28.2"

        # enable disabled sensor
        entity_id = "sensor.openevse_vehicle_charge_completion"
        entity_entry = entity_registry.async_get(entity_id)

        assert entity_entry
        assert entity_entry.disabled
        assert entity_entry.disabled_by is er.RegistryEntryDisabler.INTEGRATION

        updated_entry = entity_registry.async_update_entity(
            entity_entry.entity_id, disabled_by=None
        )
        assert updated_entry != entity_entry
        assert updated_entry.disabled is False

        # enable disabled cable temperature sensor
        cable_sensor_id = "sensor.openevse_cable_temperature_ev1"
        cable_entry = entity_registry.async_get(cable_sensor_id)
        assert cable_entry
        assert cable_entry.disabled
        assert cable_entry.disabled_by is er.RegistryEntryDisabler.INTEGRATION

        entity_registry.async_update_entity(cable_entry.entity_id, disabled_by=None)

        # reload the integration
        assert await hass.config_entries.async_forward_entry_unload(entry, "sensor")
        await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
        await hass.async_block_till_done()

        state = hass.states.get("sensor.openevse_vehicle_charge_completion")
        assert state
        assert state.state == "unknown"

        # Cable temperature sensor should be unavailable without controller 9.4.0+
        state = hass.states.get(cable_sensor_id)
        assert state
        assert state.state == "unavailable"

        # With controller 9.4.0+ and sensor data in coordinator, show value
        manager = hass.data[DOMAIN][entry.entry_id]["manager"]
        coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        with patch.object(manager, "controller_version_check", return_value=True):
            coordinator.data["cable_temperature_ev1"] = 42.5
            coordinator.async_set_updated_data(coordinator.data)
            await hass.async_block_till_done()

            state = hass.states.get(cable_sensor_id)
            assert state
            assert state.state == "42.5"


async def test_sensors_controller_v9(
    hass,
    test_charger_controller_v9,
    mock_ws_start,
    mock_aioclient,
    entity_registry: er.EntityRegistry,
    caplog,
):
    """Test sensors setup and cable temperatures with controller v9.4.0 fixture."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    with caplog.at_level(logging.DEBUG):
        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 28

        # enable disabled cable temperature sensors
        for sensor_id in (
            "sensor.openevse_cable_temperature_ev1",
            "sensor.openevse_cable_temperature_inlet_1",
        ):
            cable_entry = entity_registry.async_get(sensor_id)
            assert cable_entry
            assert cable_entry.disabled
            entity_registry.async_update_entity(cable_entry.entity_id, disabled_by=None)

        # reload sensor platform to load enabled sensors
        assert await hass.config_entries.async_forward_entry_unload(entry, "sensor")
        await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
        await hass.async_block_till_done()

        # Decoded from fixture status-controller-v9 (425 -> 42.5, 380 -> 38.0)
        state_ev1 = hass.states.get("sensor.openevse_cable_temperature_ev1")
        assert state_ev1
        assert state_ev1.state == "42.5"

        state_in1 = hass.states.get("sensor.openevse_cable_temperature_inlet_1")
        assert state_in1
        assert state_in1.state == "38.0"


async def test_sensor_coverage_icon_and_version(
    hass,
    test_charger,
    mock_ws_start,
    mock_aioclient,
):
    """Test coverage for sensor icon fallbacks and firmware version checks."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    data_entry = hass.data[DOMAIN][entry.entry_id]
    coordinator = data_entry["coordinator"]
    manager = data_entry["manager"]

    coordinator.data["state"] = "unknown_state_value"
    coordinator.async_update_listeners()
    await hass.async_block_till_done()

    state = hass.states.get("sensor.openevse_charging_status")
    assert state.attributes["icon"] == "mdi:alert-octagon"

    target_sensor = "sensor.openevse_override_state"

    with patch.object(manager, "version_check", return_value=False):
        coordinator.async_update_listeners()
        await hass.async_block_till_done()

        state = hass.states.get(target_sensor)
        assert state.state == "unavailable"

    with patch.object(manager, "version_check", return_value=True):
        coordinator.async_update_listeners()
        await hass.async_block_till_done()

        state = hass.states.get(target_sensor)
        assert state.state != "unavailable"


async def test_sensor_availability_aioclient(
    hass,
    mock_aioclient,
    mock_ws_start,
    caplog,
):
    """Test sensor availability using mock_aioclient to simulate network failure."""
    host = "openevse.test.tld"
    urls = [
        f"http://{host}/config",
        f"http://{host}/status",
        f"http://{host}/claims/target",
        f"http://{host}/override",
        f"http://{host}/",
    ]

    valid_response = {
        "mode": 1,
        "state": 2,
        "connected": 1,
        "comm_success": 1,
        "amp": 48,
        "volts": 240,
        "pilot": 48,
        "temp1": 250,
        "temp2": 260,
        "temp3": 270,
        "wattsec": 123456,
        "watthour": 123456,
        "ota_update": 0,
        "vehicle": 1,
        "manual_override": 0,
        "divert_active": 0,
        "using_ethernet": 0,
        "shaper_active": 0,
        "mqtt_connected": 0,
        "firmware": "7.1.3",
        "protocol": "1.0.0",
        "wifi_firmware": "4.1.2",
        "version": "4.1.2",
        "claims": [],
        "overrides": [],
    }

    for url in urls:
        mock_aioclient.get(url, status=200, json=valid_response)
        mock_aioclient.post(url, status=200, json=valid_response)

    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    mock_aioclient.clear_requests()

    for url in urls:
        mock_aioclient.get(url, exc=ClientError("Network Down"))
        mock_aioclient.post(url, exc=ClientError("Network Down"))

    with contextlib.suppress(ClientError):
        await coordinator.async_refresh()

    await hass.async_block_till_done()

    state = hass.states.get("sensor.openevse_charging_status")
    assert state.state == "unavailable"

    mock_aioclient.clear_requests()
    for url in urls:
        mock_aioclient.get(url, status=200, json=valid_response)
        mock_aioclient.post(url, status=200, json=valid_response)

    await coordinator.async_refresh()
    await hass.async_block_till_done()

    state = hass.states.get("sensor.openevse_charging_status")
    assert state.state != "unavailable"


async def test_vehicle_range_sensor_miles(
    hass,
    test_charger,
    mock_ws_start,
    mock_aioclient,
    entity_registry: er.EntityRegistry,
):
    """Test vehicle range sensor with miles unit and async parsing logic."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.openevse.OpenEVSE.vehicle_range_with_unit",
        new_callable=PropertyMock,
        return_value=(150, "miles"),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        # Enable vehicle range sensor (disabled by default)
        entity_id = "sensor.openevse_vehicle_range"
        entity_entry = entity_registry.async_get(entity_id)
        assert entity_entry
        entity_registry.async_update_entity(entity_id, disabled_by=None)

        # reload the integration sensor platform
        assert await hass.config_entries.async_forward_entry_unload(entry, "sensor")
        await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
        await hass.async_block_till_done()

        entity = hass.data["entity_components"]["sensor"].get_entity(entity_id)
        assert entity
        assert entity.native_unit_of_measurement == UnitOfLength.MILES

        # Test async_parse_sensors unpacking
        coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        with patch.object(
            coordinator,
            "_collect_async_values",
            return_value={"vehicle_range": (100, "miles")},
        ):
            res = await coordinator.async_parse_sensors()
            assert res["vehicle_range"] == 100


async def test_vehicle_range_sensor_km(
    hass,
    test_charger,
    mock_ws_start,
    mock_aioclient,
    entity_registry: er.EntityRegistry,
):
    """Test vehicle range sensor with km and kilometers unit mapping."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.openevse.OpenEVSE.vehicle_range_with_unit",
        new_callable=PropertyMock,
        return_value=(240, "km"),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        entity_id = "sensor.openevse_vehicle_range"
        entity_entry = entity_registry.async_get(entity_id)
        assert entity_entry
        entity_registry.async_update_entity(entity_id, disabled_by=None)

        assert await hass.config_entries.async_forward_entry_unload(entry, "sensor")
        await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
        await hass.async_block_till_done()

        entity = hass.data["entity_components"]["sensor"].get_entity(entity_id)
        assert entity
        assert entity.native_unit_of_measurement == UnitOfLength.KILOMETERS

    # Reload and test with "kilometers"
    with patch(
        "custom_components.openevse.OpenEVSE.vehicle_range_with_unit",
        new_callable=PropertyMock,
        return_value=(240, "kilometers"),
    ):
        # Trigger dynamic update check
        entity = hass.data["entity_components"]["sensor"].get_entity(entity_id)
        assert entity
        assert entity.native_unit_of_measurement == UnitOfLength.KILOMETERS


async def test_sensor_coverage_gaps(hass, test_charger, mock_ws_start):
    """Test sensor coverage gaps."""
    entry = MockConfigEntry(domain=DOMAIN, data=CONFIG_DATA)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    description_no_val_fn = MagicMock(
        key="test_sensor_key",
        name="Test Sensor",
        min_version=None,
        value_fn=None,
        native_unit_of_measurement=None,
        icon=None,
    )
    entity = OpenEVSESensor(description_no_val_fn, "test_unique_id", coordinator, entry)
    coordinator.data = {"test_sensor_key": "some_value"}
    assert entity.native_value == "some_value"

    # Test sensor min_controller_version coverage
    manager = hass.data[DOMAIN][entry.entry_id]["manager"]
    desc_controller = MagicMock(
        key="cable_temp_test",
        name="Cable Temp Test",
        min_version="5.1.0",
        min_controller_version="9.4.0",
        value_fn=None,
        native_unit_of_measurement=None,
        icon=None,
    )
    entity_controller = OpenEVSESensor(
        desc_controller, entry.entry_id, coordinator, entry
    )
    entity_controller.hass = hass
    coordinator.data["cable_temp_test"] = 25.0
    with (
        patch.object(manager, "version_check", return_value=True),
        patch.object(manager, "controller_version_check", return_value=False),
    ):
        assert entity_controller.available is False

    with (
        patch.object(manager, "version_check", return_value=True),
        patch.object(manager, "controller_version_check", return_value=True),
    ):
        assert entity_controller.available is True

    # Test coordinator parse_sensors cable_temperatures unpacking
    with patch.object(
        type(manager),
        "cable_temperatures",
        new_callable=PropertyMock,
        return_value={"ev1": 35.5, "ev2": None, "in1": 40.0, "in2": None},
    ):
        data = coordinator.parse_sensors()
        assert data.get("cable_temperature_ev1") == 35.5
        assert data.get("cable_temperature_in1") == 40.0
        assert "cable_temperature_ev2" not in data
        assert "cable_temperature_in2" not in data
