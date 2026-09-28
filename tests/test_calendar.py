"""Test OpenEVSE calendar platform."""

import datetime
from unittest.mock import AsyncMock

import pytest
from homeassistant.components.calendar import DOMAIN as CALENDAR_DOMAIN
from homeassistant.exceptions import HomeAssistantError
from openevsehttp.exceptions import CommandFailedError, UnsupportedFeature
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.openevse.const import DOMAIN, MANAGER

from .const import CONFIG_DATA

pytestmark = pytest.mark.asyncio

CHARGER_NAME = "openevse"


async def test_calendar_setup_and_events(hass, test_charger, mock_ws_start):
    """Test calendar entity setup and retrieving events."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
        version=2,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entity_ids = hass.states.async_entity_ids(CALENDAR_DOMAIN)
    assert len(entity_ids) == 1
    entity_id = entity_ids[0]

    state = hass.states.get(entity_id)
    assert state is not None
    assert state.name == "openevse Schedule"

    manager = hass.data[DOMAIN][entry.entry_id][MANAGER]

    # Mock get_schedule data
    schedule_data = [
        {
            "id": 1,
            "state": "active",
            "time": "02:00:00",
            "days": ["Monday", "Wednesday", "Friday"],
            "duration": 120,
        },
        {
            "id": 2,
            "state": "disabled",
            "time": "14:00:00",
            "days": ["Sunday"],
        },
    ]
    manager.get_schedule = AsyncMock(return_value=schedule_data)

    calendar_entity = hass.data["entity_components"][CALENDAR_DOMAIN].get_entity(
        entity_id
    )
    assert calendar_entity is not None

    # Query events across a 2-week range
    start_date = datetime.datetime(2026, 9, 21, 0, 0, tzinfo=datetime.UTC)
    end_date = datetime.datetime(2026, 10, 5, 0, 0, tzinfo=datetime.UTC)

    events = await calendar_entity.async_get_events(hass, start_date, end_date)
    assert len(events) > 0
    first_event = events[0]
    assert "OpenEVSE Charging" in first_event.summary
    assert first_event.uid is not None
    assert first_event.uid.startswith("1_") or first_event.uid.startswith("2_")

    # Verify event property when there is an upcoming event
    future_event = [
        {
            "id": 3,
            "state": "active",
            "time": "23:00:00",
            "days": [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ],
            "duration": 60,
        }
    ]
    manager.get_schedule = AsyncMock(return_value=future_event)
    calendar_entity._events_cache.clear()
    await calendar_entity.async_get_events(hass, start_date, end_date)
    assert calendar_entity.event is not None


async def test_calendar_setup_unsupported_firmware(
    hass, test_charger_v2, mock_ws_start
):
    """Test calendar entity is not loaded on firmware < 4.0.0."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
        version=2,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Firmware v2 should skip calendar registration
    assert len(hass.states.async_entity_ids(CALENDAR_DOMAIN)) == 0


async def test_calendar_create_update_delete_events(hass, test_charger, mock_ws_start):
    """Test creating, updating, and deleting events on the calendar."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
        version=2,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entity_id = "calendar.openevse_schedule"
    calendar_entity = hass.data["entity_components"][CALENDAR_DOMAIN].get_entity(
        entity_id
    )
    assert calendar_entity is not None

    manager = hass.data[DOMAIN][entry.entry_id][MANAGER]
    manager.set_schedule = AsyncMock()
    manager.delete_schedule = AsyncMock()
    manager.get_schedule = AsyncMock(return_value=[])

    # 1. Create Event
    await calendar_entity.async_create_event(
        dtstart=datetime.datetime(2026, 9, 28, 2, 0, tzinfo=datetime.UTC),
        dtend=datetime.datetime(2026, 9, 28, 4, 0, tzinfo=datetime.UTC),
        summary="Test Charge",
        rrule="FREQ=WEEKLY;BYDAY=MO,WE,FR",
    )
    manager.set_schedule.assert_awaited_once()
    payload = manager.set_schedule.await_args[0][0]
    assert payload["days"] == ["Monday", "Wednesday", "Friday"]
    assert payload["duration"] == 120

    # 2. Update Event
    manager.set_schedule.reset_mock()
    await calendar_entity.async_update_event(
        uid="5_20260928",
        event={
            "dtstart": datetime.datetime(2026, 9, 28, 3, 0, tzinfo=datetime.UTC),
            "dtend": datetime.datetime(2026, 9, 28, 4, 30, tzinfo=datetime.UTC),
            "summary": "Updated Charge",
        },
    )
    manager.set_schedule.assert_awaited_once()
    update_call_args = manager.set_schedule.await_args
    assert update_call_args[1]["event_id"] == 5
    assert update_call_args[0][0]["duration"] == 90

    # 3. Delete Event
    await calendar_entity.async_delete_event(uid="5_20260928")
    manager.delete_schedule.assert_awaited_once_with(5)

    # 4. Error cases
    with pytest.raises(HomeAssistantError, match="Event start time is required"):
        await calendar_entity.async_create_event()

    with pytest.raises(HomeAssistantError, match="Invalid event UID"):
        await calendar_entity.async_delete_event(uid="invaliduid")

    with pytest.raises(HomeAssistantError, match="Invalid event UID"):
        await calendar_entity.async_update_event(
            uid="invaliduid", event={"dtstart": datetime.datetime.now()}
        )

    with pytest.raises(HomeAssistantError, match="Event start time is required"):
        await calendar_entity.async_update_event(uid="5_20260928", event={})

    # CommandFailedError handling
    manager.set_schedule.side_effect = CommandFailedError("Simulated failure")
    with pytest.raises(HomeAssistantError, match="Failed to create schedule"):
        await calendar_entity.async_create_event(
            dtstart=datetime.datetime(2026, 9, 28, 2, 0, tzinfo=datetime.UTC)
        )

    manager.delete_schedule.side_effect = CommandFailedError("Simulated failure")
    with pytest.raises(HomeAssistantError, match="Failed to delete schedule"):
        await calendar_entity.async_delete_event(uid="5_20260928")


async def test_calendar_get_schedule_errors(hass, test_charger, mock_ws_start):
    """Test get_schedule errors gracefully handled."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
        version=2,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entity_id = "calendar.openevse_schedule"
    calendar_entity = hass.data["entity_components"][CALENDAR_DOMAIN].get_entity(
        entity_id
    )

    manager = hass.data[DOMAIN][entry.entry_id][MANAGER]

    # 1. UnsupportedFeature
    manager.get_schedule = AsyncMock(side_effect=UnsupportedFeature("get_schedule"))
    events = await calendar_entity.async_get_events(
        hass,
        datetime.datetime.now(datetime.UTC),
        datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1),
    )
    assert events == []

    # 2. General Exception
    manager.get_schedule = AsyncMock(side_effect=Exception("Network error"))
    events = await calendar_entity.async_get_events(
        hass,
        datetime.datetime.now(datetime.UTC),
        datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1),
    )
    assert events == []


async def test_calendar_edge_cases_and_caching(hass, test_charger, mock_ws_start):
    """Test calendar coverage edge cases."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CHARGER_NAME,
        data=CONFIG_DATA,
        version=2,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entity_id = "calendar.openevse_schedule"
    calendar_entity = hass.data["entity_components"][CALENDAR_DOMAIN].get_entity(
        entity_id
    )

    manager = hass.data[DOMAIN][entry.entry_id][MANAGER]

    # 1. Missing time or non-list days, malformed time
    manager.get_schedule = AsyncMock(
        return_value=[
            {"id": 10, "state": "active", "days": ["Monday"]},  # missing time
            {
                "id": 11,
                "state": "active",
                "time": "08:00:00",
                "days": "Monday",
            },  # days not list
            {"id": 12, "state": "active", "time": "invalid_time", "days": ["Monday"]},
        ]
    )
    events = await calendar_entity.async_get_events(
        hass,
        datetime.datetime(2026, 9, 21, 0, 0, tzinfo=datetime.UTC),
        datetime.datetime(2026, 9, 28, 0, 0, tzinfo=datetime.UTC),
    )
    assert events == []

    # Single mapping response (triggers line 145)
    manager.get_schedule = AsyncMock(
        return_value={
            "id": 13,
            "state": "active",
            "time": "invalid_time",
            "days": ["Monday"],
        }
    )
    calendar_entity._events_cache.clear()
    events = await calendar_entity.async_get_events(
        hass,
        datetime.datetime(2026, 9, 21, 0, 0, tzinfo=datetime.UTC),
        datetime.datetime(2026, 9, 28, 0, 0, tzinfo=datetime.UTC),
    )
    assert events == []

    # Non-list and non-mapping response
    manager.get_schedule = AsyncMock(return_value="unexpected_string")
    calendar_entity._events_cache.clear()
    events = await calendar_entity.async_get_events(
        hass,
        datetime.datetime(2026, 9, 21, 0, 0, tzinfo=datetime.UTC),
        datetime.datetime(2026, 9, 28, 0, 0, tzinfo=datetime.UTC),
    )
    assert events == []

    # 2. Schedule version caching: same version returns cache directly
    manager._status["schedule_version"] = 1
    calendar_entity._events_cache = [
        {
            "id": 11,
            "state": "active",
            "time": "08:00:00",
            "days": ["Monday"],
        }
    ]
    calendar_entity._last_schedule_version = 1
    manager.get_schedule = AsyncMock()

    events = await calendar_entity.async_get_events(
        hass,
        datetime.datetime(2026, 9, 21, 0, 0, tzinfo=datetime.UTC),
        datetime.datetime(2026, 9, 28, 0, 0, tzinfo=datetime.UTC),
    )
    assert not manager.get_schedule.called
    assert len(events) > 0

    # 3. Create & Update with datetime.date inputs and rrule without match
    manager.set_schedule = AsyncMock()
    await calendar_entity.async_create_event(
        dtstart=datetime.date(2026, 9, 28),
        dtend=datetime.date(2026, 9, 29),
        rrule="FREQ=WEEKLY;BYDAY=INVALID",
    )
    manager.set_schedule.assert_awaited_once()

    manager.set_schedule.reset_mock()
    await calendar_entity.async_update_event(
        uid="11_20260928",
        event={
            "dtstart": datetime.date(2026, 9, 28),
            "dtend": datetime.date(2026, 9, 29),
            "rrule": "FREQ=WEEKLY;BYDAY=MO,TU",
        },
    )
    manager.set_schedule.assert_awaited_once()
    assert manager.set_schedule.await_args[0][0]["days"] == ["Monday", "Tuesday"]

    # 4. Update failure handling
    manager.set_schedule.side_effect = CommandFailedError("Simulated failure")
    with pytest.raises(HomeAssistantError, match="Failed to update schedule"):
        await calendar_entity.async_update_event(
            uid="11_20260928",
            event={"dtstart": datetime.date(2026, 9, 28)},
        )
