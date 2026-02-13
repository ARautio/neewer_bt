"""Unit tests for Neewer TL40 integration behavior."""

from __future__ import annotations

import importlib
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock


def _install_homeassistant_stubs() -> None:
    homeassistant = types.ModuleType("homeassistant")
    components = types.ModuleType("homeassistant.components")
    bluetooth = types.ModuleType("homeassistant.components.bluetooth")
    light = types.ModuleType("homeassistant.components.light")
    config_entries = types.ModuleType("homeassistant.config_entries")
    ha_const = types.ModuleType("homeassistant.const")
    core = types.ModuleType("homeassistant.core")
    exceptions = types.ModuleType("homeassistant.exceptions")
    entity_platform = types.ModuleType("homeassistant.helpers.entity_platform")

    class LightEntity:
        def async_write_ha_state(self) -> None:
            self._ha_state_write_calls = getattr(self, "_ha_state_write_calls", 0) + 1

    class ColorMode:
        COLOR_TEMP = "color_temp"

    light.ATTR_BRIGHTNESS = "brightness"
    light.ATTR_COLOR_TEMP_KELVIN = "color_temp_kelvin"
    light.ColorMode = ColorMode
    light.LightEntity = LightEntity

    class ConfigEntry:
        pass

    class HomeAssistant:
        pass

    config_entries.ConfigEntry = ConfigEntry

    class Platform:
        LIGHT = "light"

    ha_const.Platform = Platform
    ha_const.CONF_ADDRESS = "address"

    core.HomeAssistant = HomeAssistant

    class ConfigEntryNotReady(Exception):
        pass

    exceptions.ConfigEntryNotReady = ConfigEntryNotReady

    def _async_ble_device_from_address(_hass, _address, _connectable):
        return None

    bluetooth.async_ble_device_from_address = _async_ble_device_from_address
    components.bluetooth = bluetooth

    entity_platform.AddEntitiesCallback = object

    sys.modules.setdefault("homeassistant", homeassistant)
    sys.modules.setdefault("homeassistant.components", components)
    sys.modules.setdefault("homeassistant.components.bluetooth", bluetooth)
    sys.modules.setdefault("homeassistant.components.light", light)
    sys.modules.setdefault("homeassistant.config_entries", config_entries)
    sys.modules.setdefault("homeassistant.const", ha_const)
    sys.modules.setdefault("homeassistant.core", core)
    sys.modules.setdefault("homeassistant.exceptions", exceptions)
    sys.modules.setdefault("homeassistant.helpers.entity_platform", entity_platform)


def _install_bleak_stubs() -> None:
    bleak = types.ModuleType("bleak")

    class BleakError(Exception):
        pass

    class BleakClient:
        def __init__(self, address: str) -> None:
            self.address = address
            self.is_connected = False

        async def connect(self) -> None:
            self.is_connected = True

        async def disconnect(self) -> None:
            self.is_connected = False

        async def write_gatt_char(self, _char, _data, response=False) -> None:
            return None

    bleak.BleakClient = BleakClient
    bleak.BleakError = BleakError

    sys.modules.setdefault("bleak", bleak)


_install_homeassistant_stubs()
_install_bleak_stubs()

light_module = importlib.import_module("custom_components.neewer_bt.light")
device_module = importlib.import_module("custom_components.neewer_bt.neewer.device")


class TestNeewerLightEntity(unittest.IsolatedAsyncioTestCase):
    async def test_turn_on_without_kwargs_uses_power_command(self) -> None:
        fake_device = SimpleNamespace(
            _device=SimpleNamespace(address="AA:BB"),
            state=False,
            turn_on=AsyncMock(),
            turn_off=AsyncMock(),
            set_cct=AsyncMock(),
        )

        entity = light_module.NeewerLight(fake_device)

        await entity.async_turn_on()

        fake_device.turn_on.assert_awaited_once()
        fake_device.set_cct.assert_not_awaited()
        self.assertTrue(entity.is_on)
        self.assertEqual(getattr(entity, "_ha_state_write_calls", 0), 1)

    async def test_turn_on_with_values_uses_cct_command(self) -> None:
        fake_device = SimpleNamespace(
            _device=SimpleNamespace(address="AA:BB"),
            state=False,
            turn_on=AsyncMock(),
            turn_off=AsyncMock(),
            set_cct=AsyncMock(),
        )

        entity = light_module.NeewerLight(fake_device)

        await entity.async_turn_on(brightness=255, color_temp_kelvin=3200)

        fake_device.turn_on.assert_not_awaited()
        fake_device.set_cct.assert_awaited_once_with(100, 32, 50)
        self.assertEqual(entity.brightness, 255)
        self.assertEqual(entity.color_temp_kelvin, 3200)
        self.assertTrue(entity.is_on)

    async def test_turn_off_uses_power_command(self) -> None:
        fake_device = SimpleNamespace(
            _device=SimpleNamespace(address="AA:BB"),
            state=True,
            turn_on=AsyncMock(),
            turn_off=AsyncMock(),
            set_cct=AsyncMock(),
        )

        entity = light_module.NeewerLight(fake_device)

        await entity.async_turn_off()

        fake_device.turn_off.assert_awaited_once()
        self.assertFalse(entity.is_on)


class TestNeewerDeviceCommands(unittest.IsolatedAsyncioTestCase):
    async def test_set_cct_clamps_values_and_sets_state(self) -> None:
        device = device_module.NeewerBTDevice(
            SimpleNamespace(address="AA:BB"), "NEEWER-TL40"
        )
        device._write_command = AsyncMock()

        await device.set_cct(300, 9999, 200)

        device._write_command.assert_awaited_once_with([120, 135, 2, 100, 56, 100])
        self.assertTrue(device.state)


if __name__ == "__main__":
    unittest.main()
