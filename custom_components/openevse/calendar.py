"""Support for OpenEVSE calendar."""

from __future__ import annotations

import contextlib
import datetime
import logging
from collections.abc import Mapping
from typing import Any

import homeassistant.util.dt as dt_util
from homeassistant.components.calendar import (
    CalendarEntity,
    CalendarEntityFeature,
    CalendarEvent,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from openevsehttp.__main__ import OpenEVSE
from openevsehttp.exceptions import CommandFailedError, UnsupportedFeature

from .const import CONF_NAME as CONF_NAME_CONST
from .entity import OpenEVSEEntity
from .logger import OpenEVSELoggerAdapter
from .models import OpenEVSEConfigEntry

_LOGGER = logging.getLogger(__name__)

WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

RRULE_TO_DAY = {
    "MO": "Monday",
    "TU": "Tuesday",
    "WE": "Wednesday",
    "TH": "Thursday",
    "FR": "Friday",
    "SA": "Saturday",
    "SU": "Sunday",
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: OpenEVSEConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenEVSE calendar platform."""
    manager: OpenEVSE = config_entry.runtime_data.manager
    coordinator: DataUpdateCoordinator = config_entry.runtime_data.coordinator

    logger = OpenEVSELoggerAdapter(
        _LOGGER, {"device_name": config_entry.data.get(CONF_NAME_CONST, "OpenEVSE")}
    )

    if not manager.version_check("4.0.0"):
        logger.debug(
            "Skipping calendar platform: firmware version does not meet minimum "
            "requirement (4.0.0)"
        )
        return

    async_add_entities(
        [OpenEVSECalendarEntity(hass, config_entry, coordinator, manager)]
    )


class OpenEVSECalendarEntity(CoordinatorEntity, OpenEVSEEntity, CalendarEntity):
    """Representation of an OpenEVSE schedule calendar entity."""

    _attr_has_entity_name = True
    _attr_name = "Schedule"
    _attr_supported_features = (
        CalendarEntityFeature.CREATE_EVENT
        | CalendarEntityFeature.DELETE_EVENT
        | CalendarEntityFeature.UPDATE_EVENT
    )

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        coordinator: DataUpdateCoordinator,
        manager: OpenEVSE,
    ) -> None:
        """Initialize the OpenEVSE calendar."""
        super().__init__(coordinator)
        self.hass = hass
        self._config = config_entry
        self.manager = manager
        self._base_unique_id = config_entry.entry_id
        self._attr_unique_id = f"{self._base_unique_id}.calendar"
        self._attr_name = "Schedule"
        self.logger = OpenEVSELoggerAdapter(
            _LOGGER,
            {"device_name": config_entry.data.get(CONF_NAME_CONST, "OpenEVSE")},
        )
        self._events_cache: list[dict[str, Any]] = []
        self._last_schedule_version: int | None = None

    @property
    def _local_tz(self) -> datetime.tzinfo:
        """Return the configured Home Assistant local timezone."""
        return dt_util.get_time_zone(self.hass.config.time_zone)

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming or currently active event."""
        now = dt_util.now()
        upcoming = self._resolve_events(
            now - datetime.timedelta(days=1), now + datetime.timedelta(days=7)
        )
        # Filter events that haven't ended yet
        valid_events = [e for e in upcoming if e.end_datetime_local > now]
        if not valid_events:
            return None
        # Sort by start datetime
        valid_events.sort(key=lambda e: e.start_datetime_local)
        return valid_events[0]

    async def _async_get_schedule_data(self) -> list[dict[str, Any]]:
        """Fetch schedule events from charger with version-aware caching."""
        current_version = getattr(self.manager, "schedule_version", None)
        if (
            self._events_cache
            and current_version is not None
            and current_version == self._last_schedule_version
        ):
            return self._events_cache

        try:
            raw_schedule = await self.manager.get_schedule()
        except UnsupportedFeature:
            self.logger.debug("get_schedule is not supported on this firmware version")
            return []
        except Exception as err:
            self.logger.warning(
                "Error fetching schedule from OpenEVSE (%s): %s",
                type(err).__name__,
                err,
            )
            return self._events_cache

        if isinstance(raw_schedule, list):
            self._events_cache = [
                dict(item) for item in raw_schedule if isinstance(item, Mapping)
            ]
        elif isinstance(raw_schedule, Mapping):
            self._events_cache = [dict(raw_schedule)]
        else:
            self._events_cache = []

        self._last_schedule_version = current_version
        return self._events_cache

    def _resolve_events(
        self,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> list[CalendarEvent]:
        """Expand weekly schedule items into concrete CalendarEvents."""
        events: list[CalendarEvent] = []
        local_tz = self._local_tz

        # Convert query range boundaries to local date
        start_local = start_date.astimezone(local_tz)
        end_local = end_date.astimezone(local_tz)

        curr_date = start_local.date()
        end_d = end_local.date()

        for item in self._events_cache:
            event_id = item.get("id")
            time_str = item.get("time")
            days = item.get("days", [])
            state = item.get("state", "active")

            if not time_str or not isinstance(days, list):
                continue

            try:
                time_parts = [int(p) for p in time_str.split(":")]
                event_time = datetime.time(
                    time_parts[0],
                    time_parts[1],
                    time_parts[2] if len(time_parts) > 2 else 0,
                    tzinfo=local_tz,
                )
            except (ValueError, IndexError):
                continue

            # Default duration: 1 hour if not specified
            duration_minutes = 60
            if "duration" in item:
                with contextlib.suppress(ValueError, TypeError):
                    duration_minutes = int(item["duration"])

            # Map weekday strings
            normalized_days = {d.capitalize() for d in days if isinstance(d, str)}

            step_date = curr_date
            while step_date <= end_d:
                weekday_name = WEEKDAYS[step_date.weekday()]
                if weekday_name in normalized_days:
                    dt_start = datetime.datetime.combine(
                        step_date, event_time, tzinfo=local_tz
                    )
                    dt_end = dt_start + datetime.timedelta(minutes=duration_minutes)

                    if dt_start < end_local and dt_end > start_local:
                        uid = f"{event_id}_{step_date.strftime('%Y%m%d')}"
                        summary = f"OpenEVSE Charging ({state.capitalize()})"
                        description = f"Schedule ID: {event_id}\nState: {state}"
                        events.append(
                            CalendarEvent(
                                start=dt_start,
                                end=dt_end,
                                summary=summary,
                                description=description,
                                uid=uid,
                            )
                        )
                step_date += datetime.timedelta(days=1)

        return events

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        await self._async_get_schedule_data()
        return self._resolve_events(start_date, end_date)

    @staticmethod
    def _extract_event_id(uid: str) -> int:
        """Extract the integer schedule ID from a calendar event UID."""
        try:
            return int(uid.split("_", maxsplit=1)[0])
        except (ValueError, IndexError) as err:
            raise HomeAssistantError(
                f"Invalid event UID '{uid}': cannot extract event ID"
            ) from err

    def _to_local_datetime(
        self, dt_or_date: datetime.datetime | datetime.date
    ) -> datetime.datetime:
        """Normalize a date or datetime to the configured local timezone."""
        local_tz = self._local_tz
        if isinstance(dt_or_date, datetime.date) and not isinstance(
            dt_or_date, datetime.datetime
        ):
            dt_or_date = datetime.datetime.combine(
                dt_or_date, datetime.time.min, tzinfo=local_tz
            )
        return dt_or_date.astimezone(local_tz)

    def _build_schedule_payload(
        self,
        event_data: Mapping[str, Any],
        event_id: int | None = None,
    ) -> dict[str, Any]:
        """Build an OpenEVSE schedule payload from Home Assistant event data."""
        start_dt = event_data.get("dtstart")
        if not start_dt:
            raise HomeAssistantError("Event start time is required")

        start_local = self._to_local_datetime(start_dt)
        days = [WEEKDAYS[start_local.weekday()]]

        rrule_str = event_data.get("rrule")
        if rrule_str and "BYDAY=" in rrule_str:
            byday_part = rrule_str.split("BYDAY=")[1].split(";")[0]
            parsed_days = [
                RRULE_TO_DAY[d] for d in byday_part.split(",") if d in RRULE_TO_DAY
            ]
            if parsed_days:
                days = parsed_days

        event_payload: dict[str, Any] = {
            "state": "active",
            "time": start_local.strftime("%H:%M:%S"),
            "days": days,
        }
        if event_id is not None:
            event_payload["id"] = event_id

        if end_dt := event_data.get("dtend"):
            end_local = self._to_local_datetime(end_dt)
            duration_minutes = int((end_local - start_local).total_seconds() // 60)
            if duration_minutes > 0:
                event_payload["duration"] = duration_minutes

        return event_payload

    async def async_create_event(self, **kwargs: Any) -> None:
        """Add a new schedule event to OpenEVSE."""
        event_payload = self._build_schedule_payload(kwargs)

        try:
            await self.manager.set_schedule(event_payload)
        except (CommandFailedError, Exception) as err:
            self.logger.error(
                "Failed to create OpenEVSE schedule (%s): %s",
                type(err).__name__,
                err,
            )
            raise HomeAssistantError(f"Failed to create schedule: {err}") from err

        self._events_cache.clear()
        await self.coordinator.async_refresh()

    async def async_delete_event(
        self,
        uid: str,
        recurrence_id: str | None = None,
        recurrence_range: str | None = None,
    ) -> None:
        """Delete an event on the calendar."""
        event_id = self._extract_event_id(uid)

        try:
            await self.manager.delete_schedule(event_id)
        except (CommandFailedError, Exception) as err:
            self.logger.error(
                "Failed to delete OpenEVSE schedule %s (%s): %s",
                event_id,
                type(err).__name__,
                err,
            )
            raise HomeAssistantError(f"Failed to delete schedule: {err}") from err

        self._events_cache.clear()
        await self.coordinator.async_refresh()

    async def async_update_event(
        self,
        uid: str,
        event: dict[str, Any],
        recurrence_id: str | None = None,
        recurrence_range: str | None = None,
    ) -> None:
        """Update an event on the calendar."""
        event_id = self._extract_event_id(uid)
        event_payload = self._build_schedule_payload(event, event_id=event_id)

        try:
            await self.manager.set_schedule(event_payload, event_id=event_id)
        except (CommandFailedError, Exception) as err:
            self.logger.error(
                "Failed to update OpenEVSE schedule %s (%s): %s",
                event_id,
                type(err).__name__,
                err,
            )
            raise HomeAssistantError(f"Failed to update schedule: {err}") from err

        self._events_cache.clear()
        await self.coordinator.async_refresh()
