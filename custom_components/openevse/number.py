"""Support for OpenEVSE controls using the number platform."""

from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import (
    OpenEVSEManager,
    OpenEVSEUpdateCoordinator,
)
from .const import CONF_NAME, COORDINATOR, DOMAIN, MANAGER, NUMBER_TYPES
from .entity import OpenEVSENumberEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenEVSE Number entity from Config Entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    manager = hass.data[DOMAIN][config_entry.entry_id][MANAGER]

    entities: list[NumberEntity] = []

    for number in NUMBER_TYPES:
        entities.append(
            OpenEVSENumberEntity(
                config_entry, coordinator, NUMBER_TYPES[number], manager
            )
        )
    async_add_entities(entities)


class OpenEVSENumberEntity(CoordinatorEntity, NumberEntity):
    """Representation of a OpenEVSE number entity."""

    def __init__(
        self,
        config_entry: ConfigEntry,
        coordinator: OpenEVSEUpdateCoordinator,
        description: OpenEVSENumberEntityDescription,
        manager: OpenEVSEManager,
    ) -> None:
        """Initialize a ZwaveNumberEntity entity."""
        super().__init__(coordinator)
        self._description = description
        self._unique_id = config_entry.entry_id
        self._config = config_entry
        self._name = description.name
        self._type = description.key
        self.coordinator = coordinator
        self._command = description.command
        self._min = description.min
        self._max = description.max
        self._value = description.value
        self._manager = manager
        # Entity class attributes
        self._attr_name = f"{config_entry.data[CONF_NAME]} {self._name}"
        self._attr_unique_id = f"{self._name}_{self._unique_id}"
        self._attr_native_step = 1.0

    @property
    def device_info(self):
        """Return a port description for device registry."""
        info = {
            "manufacturer": "OpenEVSE",
            "name": self._config.data[CONF_NAME],
            "connections": {(DOMAIN, self._config.entry_id)},
        }
        return info

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        data = self.coordinator.data
        if not isinstance(data, dict):
            return self.coordinator.last_update_success
        attributes = ("divertmode", "divert_active")
        if (
            set(attributes).issubset(data.keys())
            and self._type == "max_current_soft"
            and data["divert_active"]
            and data["divertmode"] == "eco"
        ):
            _LOGGER.debug(
                "Disabling %s due to PV Divert being active.", self._attr_name
            )
            return False
        return self.coordinator.last_update_success

    @property
    def native_min_value(self) -> float:
        """Return the minimum value."""
        min_ = self.coordinator.data.get("min_amps") if self.coordinator.data else None
        if min_ is None:
            min_ = self._min
        return float(min_ if min_ is not None else 6)

    @property
    def native_max_value(self) -> float:
        """Return the maximum value."""
        max_ = self.coordinator.data.get("max_amps") if self.coordinator.data else None
        if max_ is None:
            max_ = self._max
        return float(max_ if max_ is not None else 48)

    @property
    def native_value(self) -> float | None:
        """Return the entity value."""
        data = self.coordinator.data
        value = None
        if data is not None and self._type in data:
            value = data[self._type]
        _LOGGER.debug("Number [%s] updated value: %s", self._type, value)
        return None if value is None else float(value)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement of this entity, if any."""
        unit = self._description.native_unit_of_measurement
        return None if unit is None else str(unit)

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        temp = float(value)
        if not temp.is_integer():
            raise ValueError("charge rate must be whole amps")
        _LOGGER.debug("Command: %s Value: %s", self._command, temp)
        await getattr(self._manager, self._command)(int(temp))
