"""Support for OpenEVSE entities."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.switch import SwitchEntityDescription


@dataclass
class OpenEVSESelectEntityDescription(SelectEntityDescription):
    """Class describing OpenEVSE select entities."""

    command: str | None = None
    default_options: list | None = None


@dataclass
class OpenEVSESwitchEntityDescription(SwitchEntityDescription):
    """Class describing OpenEVSE select entities."""

    on_command: str | None = None
    off_command: str | None = None
    toggle_command: str | None = None
