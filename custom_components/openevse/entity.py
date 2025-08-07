"""Support for OpenEVSE entities."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.light import LightEntityDescription
from homeassistant.components.number import NumberEntityDescription
from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.switch import SwitchEntityDescription


@dataclass
class OpenEVSESelectEntityDescription(SelectEntityDescription):
    """Class describing OpenEVSE select entities."""

    command: str | None = None
    default_options: list | None = None
    is_async_value: bool | None = False
    value: int | None = None
    min_version: str | None = None


@dataclass
class OpenEVSESwitchEntityDescription(SwitchEntityDescription):
    """Class describing OpenEVSE select entities."""

    toggle_command: str | None = None
    min_version: str | None = None


@dataclass
class OpenEVSENumberEntityDescription(NumberEntityDescription):
    """Class describing OpenEVSE number entities."""

    command: str | None = None
    default_options: list | None = None
    min: int | None = None
    max: int | None = None
    is_async_value: bool | None = False
    value: int | None = None


@dataclass
class OpenEVSELightEntityDescription(LightEntityDescription):
    """Class describing OpenEVSE light entities."""

    command: str | None = None
    min_version: str | None = None


@dataclass
class OpenEVSESensorEntityDescription(SensorEntityDescription):
    """Class describing OpenEVSE sensor entities."""

    is_async_value: bool | None = False
    value: int | None = None
    min_version: str | None = None
