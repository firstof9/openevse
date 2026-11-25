"""Support for OpenEVSE switches."""

from __future__ import annotations

import logging
from typing import Any, cast

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import CONNECTION_ERRORS, OpenEVSEManager, OpenEVSEUpdateCoordinator
from .const import CONNECTION_ERROR, SWITCH_TYPES
from .entity import OpenEVSEEntity, OpenEVSESwitchEntityDescription
from .models import OpenEVSEConfigEntry

_LOGGER = logging.getLogger(__name__)
SLEEP_STATE = "sleeping"
ATTR_STATE = "state"
BOOLEAN_TOGGLE_COMMANDS = {
    "set_shaper",
    "set_mqtt_vehicle_range_miles",
    "set_rfid_enabled",
    "set_cable_temp_enabled",
}


async def async_setup_entry(
    hass: HomeAssistant, entry: OpenEVSEConfigEntry, async_add_entities
):
    """Set up the OpenEVSE switches."""
    coordinator = entry.runtime_data.coordinator
    manager = entry.runtime_data.manager

    switches = []
    for description in SWITCH_TYPES:
        switches.append(OpenEVSESwitch(hass, entry, coordinator, description, manager))

    async_add_entities(switches, False)


class OpenEVSESwitch(CoordinatorEntity, OpenEVSEEntity, SwitchEntity):
    """Representation of the value of a OpenEVSE Switch."""

    def __init__(
        self,
        hass,
        config_entry: OpenEVSEConfigEntry,
        coordinator: OpenEVSEUpdateCoordinator,
        description: OpenEVSESwitchEntityDescription,
        manager: OpenEVSEManager,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.hass = hass
        self._config = config_entry
        self.coordinator = coordinator
        self.entity_description = description
        self._type = description.key
        self._unique_id = config_entry.entry_id
        self._attr_name = f"{config_entry.data[CONF_NAME]} {description.name}"
        self._attr_unique_id = f"{self._attr_name}_{config_entry.entry_id}"
        self._manager = manager
        self._state = None
        self.toggle_command = description.toggle_command
        self._min_version = description.min_version
        self._min_controller_version = getattr(
            description, "min_controller_version", None
        )

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return f"{self._attr_name}_{self._attr_unique_id}"

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._attr_name

    @property
    def is_on(self) -> bool | None:
        """Return True if switch is on."""
        _, val = self._get_description_value()
        if val is None:
            self.coordinator.logger.warning("switch [%s] not supported.", self._type)
            return None

        self.coordinator.logger.debug("switch [%s]: %s", self._attr_name, val)
        if self._type == ATTR_STATE:
            return val == SLEEP_STATE
        return cast(bool, val == 1)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._check_version_supported(self._manager)

    async def _async_set_switch_state(self, turn_on: bool) -> None:
        """Set the switch state on the charger."""
        if self.is_on is turn_on:
            return
        try:
            if self.toggle_command == "claim":
                if turn_on:
                    await self._manager.release_claim()
                else:
                    await self._manager.make_claim(state="active")
            elif self.toggle_command in BOOLEAN_TOGGLE_COMMANDS:
                await getattr(self._manager, self.toggle_command)(turn_on)
            else:
                await getattr(self._manager, self.toggle_command)()
        except CONNECTION_ERRORS as err:
            self.coordinator.logger.error(CONNECTION_ERROR, err)
            raise HomeAssistantError(
                f"Error connecting to device: {err}, "
                "please check your network connection."
            ) from err

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self._async_set_switch_state(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self._async_set_switch_state(False)
