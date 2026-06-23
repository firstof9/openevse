"""Support for OpenEVSE entities."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.light import LightEntityDescription
from homeassistant.components.number import NumberEntityDescription
from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.helpers.device_registry import DeviceInfo


class OpenEVSEEntity:
    """Base class for OpenEVSE entities."""

    _config: ConfigEntry

    @property
    def device_info(self) -> DeviceInfo:
        """Return a port description for device registry."""
        return DeviceInfo(
            manufacturer="OpenEVSE",
            name=self._config.data.get(CONF_NAME),
            connections={("openevse", self._config.entry_id)},
        )


@dataclass
class OpenEVSESelectEntityDescription(SelectEntityDescription):
    """Class describing OpenEVSE select entities."""

    command: str | None = None
    default_options: list | None = None
    is_async_value: bool | None = False
    value: str | None = None
    min_version: str | None = None
    value_fn: Callable[[dict[str, Any]], Any] | None = None


@dataclass
class OpenEVSESwitchEntityDescription(SwitchEntityDescription):
    """Class describing OpenEVSE select entities."""

    toggle_command: str | None = None
    min_version: str | None = None
    value_fn: Callable[[dict[str, Any]], Any] | None = None


@dataclass
class OpenEVSENumberEntityDescription(NumberEntityDescription):
    """Class describing OpenEVSE number entities."""

    command: str | None = None
    default_options: list | None = None
    min: int | None = None
    max: int | None = None
    is_async_value: bool | None = False
    value: str | None = None
    value_fn: Callable[[dict[str, Any]], Any] | None = None


@dataclass
class OpenEVSELightEntityDescription(LightEntityDescription):
    """Class describing OpenEVSE light entities."""

    command: str | None = None
    min_version: str | None = None
    value_fn: Callable[[dict[str, Any]], Any] | None = None


@dataclass
class OpenEVSESensorEntityDescription(SensorEntityDescription):
    """Class describing OpenEVSE sensor entities."""

    is_async_value: bool | None = False
    value: str | None = None
    min_version: str | None = None
    value_fn: Callable[[dict[str, Any]], Any] | None = None


@dataclass
class OpenEVSEBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing OpenEVSE binary sensor entities."""

    is_async_value: bool | None = False
    value: str | None = None
    min_version: str | None = None
    value_fn: Callable[[dict[str, Any]], Any] | None = None
