"""Models for the OpenEVSE integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry

if TYPE_CHECKING:
    from openevsehttp.__main__ import OpenEVSE

    from . import OpenEVSEFirmwareCheck, OpenEVSEUpdateCoordinator

type OpenEVSEConfigEntry = ConfigEntry[OpenEVSEData]


@dataclass
class OpenEVSEData:
    """Runtime data stored in ConfigEntry.runtime_data."""

    coordinator: OpenEVSEUpdateCoordinator
    manager: OpenEVSE
    fw_coordinator: OpenEVSEFirmwareCheck
    unsub_listeners: list[Callable[[], None]] = field(default_factory=list)
