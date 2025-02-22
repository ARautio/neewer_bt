"""Support for Neewer Bluetooth lights."""
from __future__ import annotations

from typing import Any

from homeassistant.components.light import LightEntity, ColorMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .neewer.device import NeewerBTDevice

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Neewer Light."""
    device = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NeewerLight(device)])

class NeewerLight(LightEntity):
    """Representation of a Neewer Bluetooth Light."""

    _attr_color_mode = ColorMode.ONOFF
    _attr_supported_color_modes = {ColorMode.ONOFF}

    def __init__(self, device: NeewerBTDevice) -> None:
        """Initialize the light."""
        self._device = device
        self._attr_unique_id = device._device.address
        self._attr_name = "Neewer Light"

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._device.state

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._device.state

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        await self._device.turn_on()
        self._device.state = True

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        await self._device.turn_off()
        self._device.state = False