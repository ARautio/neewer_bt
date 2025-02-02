"""Support for NeewerBT lights."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    LightEntity,
    ColorMode
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, CONF_NAME, CONF_MODEL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MANUFACTURER, MODELS
from .coordinator import NeewerBTCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Neewer light."""
    coordinator: NeewerBTCoordinator = config_entry.runtime_data.coordinator
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([NeewerLight(coordinator, config_entry)])

class NeewerLight(LightEntity):
    """Neewer TL40 light."""

    _attr_supported_color_modes = {ColorMode.ONOFF}
    _attr_color_mode = ColorMode.ONOFF
    _attr_has_entity_name = True

    def __init__(self, coordinator: NeewerBTCoordinator, entry: ConfigEntry) -> None:
        """Initialize the light."""
        self._coordinator = coordinator
        self._attr_unique_id = entry.data[CONF_ADDRESS]
        self._attr_name = entry.data[CONF_NAME]
        self._model = entry.data[CONF_MODEL]
        self._model_info = MODELS.get(self._model, MODELS["NEEWER_TL40"])

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id)},
            name=self._attr_name,
            manufacturer=MANUFACTURER,
            model=self._model_info["name"],
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._coordinator.data.state

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on light."""
        await self._coordinator.turn_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off light."""
        await self._coordinator.turn_off()