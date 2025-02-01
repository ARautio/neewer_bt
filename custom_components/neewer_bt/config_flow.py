"""Config flow for Neewer devices."""
from __future__ import annotations
from typing import Any


from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ADDRESS, CONF_NAME, CONF_MODEL
from homeassistant.data_entry_flow import FlowResult

import voluptuous as vol

from .const import DOMAIN, LOCAL_NAMES

class NeewerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Neewer devices."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the flow."""
        self.discovered_device: BluetoothServiceInfoBleak | None = None
        self.model: str | None = None

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle the bluetooth discovery step."""
        NEEWER_PREFIXES = list(LOCAL_NAMES)

        if not any(
            discovery_info.name.startswith(prefix) 
            for prefix in NEEWER_PREFIXES
        ):
            return self.async_abort(reason="not_supported_device")

        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        self.discovered_device = discovery_info
        self.model = next(
            (prefix for prefix in NEEWER_PREFIXES if discovery_info.name.startswith(prefix)),
            "unknown"
        )
        self.context["title_placeholders"] = {"name": self.model}

        return await self.async_step_user()
    
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle user input for device name."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required(CONF_NAME, default=self.discovered_device.name): str,
                }),
            )

        return self.async_create_entry(
            title=user_input[CONF_NAME],
            data={
                CONF_ADDRESS: self.discovered_device.address,
                CONF_NAME: user_input[CONF_NAME],
                CONF_MODEL: self.model,
            },
        )