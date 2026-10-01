"""Repairs implementation for OpenEVSE."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.repairs import ConfirmRepairFlow, RepairsFlow
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from openevsehttp.exceptions import CommandFailedError

from .const import CONNECTION_ERRORS, DOMAIN, MANAGER

_LOGGER = logging.getLogger(__name__)


class NotificationAcknowledgeRepairFlow(RepairsFlow):
    """Handler for acknowledging an OpenEVSE advisory notification."""

    def __init__(self, entry_id: str, notification_id: str) -> None:
        """Initialize the repair flow."""
        self._entry_id = entry_id
        self._notification_id = notification_id
        super().__init__()

    async def async_step_init(self, user_input: dict[str, str] | None = None) -> Any:
        """Handle the first step of the repair flow."""
        return await self.async_step_confirm(user_input)

    async def async_step_confirm(self, user_input: dict[str, str] | None = None) -> Any:
        """Handle confirmation and acknowledge the notification."""
        if user_input is not None:
            manager = (
                self.hass.data.get(DOMAIN, {}).get(self._entry_id, {}).get(MANAGER)
            )
            if manager is not None:
                try:
                    await manager.acknowledge_notification(self._notification_id)
                except (*CONNECTION_ERRORS, CommandFailedError) as err:
                    _LOGGER.error(
                        "Failed to acknowledge notification %s: %s",
                        self._notification_id,
                        err,
                    )
            return self.async_create_entry(title="", data={})

        return self.async_show_form(step_id="confirm")


async def async_create_fix_flow(
    hass: HomeAssistant,
    issue_id: str,
    data: dict[str, str | int | float | None] | None,
) -> RepairsFlow:
    """Create a fix flow for an OpenEVSE issue."""
    if data is not None and "notification_id" in data and "entry_id" in data:
        return NotificationAcknowledgeRepairFlow(
            str(data["entry_id"]), str(data["notification_id"])
        )
    return ConfirmRepairFlow()


def async_process_notifications(
    hass: HomeAssistant,
    entry_id: str,
    notifications_data: dict[str, Any] | None,
) -> set[str]:
    """Process active advisory notifications and update repairs issues."""
    active_issue_ids: set[str] = set()

    if not isinstance(notifications_data, dict):
        return active_issue_ids

    notifications = notifications_data.get("notifications")
    if not isinstance(notifications, list):
        return active_issue_ids

    for item in notifications:
        if not isinstance(item, dict):
            continue
        notif_id = item.get("id")
        if not notif_id or not isinstance(notif_id, str):
            continue

        # If already acknowledged or muted, do not create or keep active repair issue
        if item.get("acked"):
            continue

        issue_id = f"advisory_{entry_id}_{notif_id}"
        active_issue_ids.add(issue_id)

        severity_str = str(item.get("severity", "warning")).lower()
        if severity_str == "critical":
            severity = ir.IssueSeverity.CRITICAL
        elif severity_str == "error":
            severity = ir.IssueSeverity.ERROR
        else:
            severity = ir.IssueSeverity.WARNING

        category = str(item.get("category", "advisory"))

        ir.async_create_issue(
            hass,
            DOMAIN,
            issue_id,
            is_fixable=True,
            is_persistent=False,
            severity=severity,
            translation_key="advisory_notification",
            translation_placeholders={
                "id": notif_id,
                "category": category,
                "severity": severity_str,
            },
            data={"entry_id": entry_id, "notification_id": notif_id},
        )

    return active_issue_ids
