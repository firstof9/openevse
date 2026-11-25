"""Support for OpenEVSE entities."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.button import ButtonEntityDescription
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
    coordinator: Any
    entity_description: Any
    _type: str
    _min_version: str | None = None
    _min_controller_version: str | None = None

    @property
    def device_info(self) -> DeviceInfo:
        """Return a port description for device registry."""
        return DeviceInfo(
            manufacturer="OpenEVSE",
            name=self._config.data.get(CONF_NAME),
            connections={("openevse", self._config.entry_id)},
        )

    @property
    def coordinator_data(self) -> dict[str, Any]:
        """Return the coordinator data as a dictionary."""
        data = self.coordinator.data
        return data if isinstance(data, dict) else {}

    def _get_description_value(self) -> tuple[bool, Any]:
        """Return (found, value) from coordinator_data via value_fn or key lookup."""
        data = self.coordinator_data
        value_fn = getattr(self.entity_description, "value_fn", None)
        if value_fn is not None:
            return True, value_fn(data)
        if self._type in data:
            return True, data[self._type]
        return False, None

    def _check_version_supported(self, manager: Any) -> bool:
        """Check if firmware and controller versions meet entity requirements."""
        if (
            self._min_version
            and manager is not None
            and not manager.version_check(self._min_version)
        ):
            return False
        return not (
            self._min_controller_version
            and manager is not None
            and not manager.controller_version_check(self._min_controller_version)
        )

    def _is_disabled_by_pv_divert(self) -> bool:
        """Return True if max_current_soft is disabled by active PV Divert."""
        data = self.coordinator_data
        if (
            self._type == "max_current_soft"
            and {"divertmode", "divert_active"}.issubset(data.keys())
            and data["divert_active"]
            and data["divertmode"] == "eco"
        ):
            self.coordinator.logger.debug(
                "Disabling %s due to PV Divert being active.",
                getattr(self, "_attr_name", self._type),
            )
            return True
        return False


@dataclass
class OpenEVSEButtonEntityDescription(ButtonEntityDescription):
    """Class describing OpenEVSE button entities."""

    min_version: str | None = None
    min_controller_version: str | None = None
    action: Callable[[Any], Coroutine[Any, Any, None]] | None = None


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
    min_controller_version: str | None = None
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
    min_controller_version: str | None = None
    value_fn: Callable[[dict[str, Any]], Any] | None = None


@dataclass
class OpenEVSEBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing OpenEVSE binary sensor entities."""

    is_async_value: bool | None = False
    value: str | None = None
    min_version: str | None = None
    value_fn: Callable[[dict[str, Any]], Any] | None = None
