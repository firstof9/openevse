"""Support for OpenEVSE entities."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.light import LightEntityDescription
from homeassistant.components.number import NumberEntityDescription
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

    toggle_command: str | None = None


@dataclass
class OpenEVSENumberEntityDescription(NumberEntityDescription):
    """Class describing OpenEVSE number entities."""

    command: str | None = None
    default_options: list | None = None
    min: int | None = None
    max: int | None = None


@dataclass
class OpenEVSELightEntityDescription(LightEntityDescription):
    """Class describing OpenEVSE light entities."""

    command: str | None = None
