"""The Neewer Bluetooth integration."""
from __future__ import annotations

import logging

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .neewer.device import NeewerBTDevice

PLATFORMS: list[Platform] = [Platform.LIGHT]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Neewer BT from a config entry."""
    address = entry.data[CONF_ADDRESS]
    model = "NEEWER-TL40"

    ble_device = bluetooth.async_ble_device_from_address(hass, address.upper(), True)
    if not ble_device:
        raise ConfigEntryNotReady(
            f"Could not find Neewer BT device with address {address}"
        )

    device = NeewerBTDevice(ble_device, model)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = device

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok