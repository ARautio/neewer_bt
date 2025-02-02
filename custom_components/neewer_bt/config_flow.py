"""Config flow for Neewer Bluetooth."""
from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.components import bluetooth
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_ADDRESS, CONF_MODEL

from .const import DOMAIN, LOCAL_NAMES

class NeewerBTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Neewer Bluetooth."""

    VERSION = 1

    async def async_step_bluetooth(self, discovery_info: bluetooth.BluetoothServiceInfoBleak) -> FlowResult:
        """Handle the bluetooth discovery step."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        return await self.async_step_confirm(
            {
                "title": discovery_info.name,
                "address": discovery_info.address,
                "model": discovery_info.name,
            }
        )

    async def async_step_confirm(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Confirm the setup."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["title"],
                data={
                    [CONF_ADDRESS]: user_input[CONF_ADDRESS],
                    [CONF_MODEL]: user_input[CONF_MODEL],
                },
            )

        return self.async_show_form(step_id="confirm")