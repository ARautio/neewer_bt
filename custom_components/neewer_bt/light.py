"""Support for Neewer Bluetooth lights."""

from __future__ import annotations

from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .neewer.device import NeewerBTDevice

TL40_MIN_TEMP_VALUE = 32
TL40_MAX_TEMP_VALUE = 56
TL40_DEFAULT_TEMP_VALUE = 56
TL40_DEFAULT_GM = 50

TL40_MIN_KELVIN = TL40_MIN_TEMP_VALUE * 100
TL40_MAX_KELVIN = TL40_MAX_TEMP_VALUE * 100
TL40_DEFAULT_BRIGHTNESS = 128


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

    _attr_color_mode = ColorMode.COLOR_TEMP
    _attr_supported_color_modes = {ColorMode.COLOR_TEMP}
    _attr_min_color_temp_kelvin = TL40_MIN_KELVIN
    _attr_max_color_temp_kelvin = TL40_MAX_KELVIN

    def __init__(self, device: NeewerBTDevice) -> None:
        """Initialize the light."""
        self._device = device
        self._attr_unique_id = device._device.address
        self._attr_name = "Neewer Light"
        self._brightness = TL40_DEFAULT_BRIGHTNESS
        self._color_temp_kelvin = TL40_DEFAULT_TEMP_VALUE * 100

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._device.state

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the light."""
        return self._brightness

    @property
    def color_temp_kelvin(self) -> int | None:
        """Return the color temperature in kelvin."""
        return self._color_temp_kelvin

    @staticmethod
    def _ha_brightness_to_device(brightness: int) -> int:
        """Convert Home Assistant brightness (0-255) to device value (0-100)."""
        return max(0, min(100, round((brightness / 255) * 100)))

    @staticmethod
    def _kelvin_to_device_temp(kelvin: int) -> int:
        """Convert kelvin to TL40 temperature units (32-56)."""
        return max(TL40_MIN_TEMP_VALUE, min(TL40_MAX_TEMP_VALUE, round(kelvin / 100)))

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS, self._brightness)
        color_temp_kelvin = kwargs.get(ATTR_COLOR_TEMP_KELVIN, self._color_temp_kelvin)

        if ATTR_BRIGHTNESS in kwargs or ATTR_COLOR_TEMP_KELVIN in kwargs:
            device_brightness = self._ha_brightness_to_device(brightness)
            device_temp = self._kelvin_to_device_temp(color_temp_kelvin)
            await self._device.set_cct(device_brightness, device_temp, TL40_DEFAULT_GM)
            self._brightness = brightness
            self._color_temp_kelvin = device_temp * 100
        else:
            await self._device.turn_on()

        self._device.state = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        await self._device.turn_off()
        self._device.state = False
        self.async_write_ha_state()
