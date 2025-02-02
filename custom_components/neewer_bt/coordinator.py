from dataclasses import dataclass
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, CONF_NAME, CONF_MODEL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.components import bluetooth

from .const import DOMAIN
from .neewer.device import NeewerBTDevice


import logging
_LOGGER = logging.getLogger(__name__)

@dataclass
class NeewerBTData:
    """Class to hold api data."""
    state: bool | None = None

class NeewerBTCoordinator(DataUpdateCoordinator):
    """Neewer BT coordinator."""

    data: NeewerBTData

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize coordinator."""

        # Set variables from values entered in config flow setup
        self.device_name = config_entry.data[CONF_NAME]
        self.device_address = config_entry.data[CONF_ADDRESS]

        ble_device = bluetooth.async_ble_device_from_address(
            hass,
            self.device_address,
            connectable=True
        )
        assert ble_device
        self._device = NeewerBTDevice(ble_device, config_entry.data[CONF_MODEL])

        # Initialise DataUpdateCoordinator
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({config_entry.unique_id})",
            update_method=self._async_update_data,
        )

    async def turn_on(self) -> None:
        """Turn the device on."""
        await self._device.turn_on()
        self.data.state = True
        self.async_set_updated_data(self.data)

    async def turn_off(self) -> None:
        """Turn the device off."""
        await self._device.turn_off()
        self.data.state = False
        self.async_set_updated_data(self.data)

    async def _async_update_data(self):
        data = NeewerBTData()
        # Fix this if we find a way to fetch data
        data.state = False
        return data