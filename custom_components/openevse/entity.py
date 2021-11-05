"""Support for OpenEVSE entities."""
from __future__ import annotations

from dataclasses import dataclass
from homeassistant.components.select import SelectEntityDescription


@dataclass
class OpenEVSESelectEntityDescription(SelectEntityDescription):
    """Class describing OpenEVSE select entities."""

    command: str | None = None
    default_options: list | None = None
