from typing import Dict

from custom_components.neewer_bt.const import MODELS

class NeewerBTDevice:
    """Handle Neewer device commands."""
    
    def __init__(self, device, model: str):
        self._device = device
        self._model_info = MODELS[model]
        self._char_write = self._model_info["char_write"]
    
    async def turn_on(self) -> None:
        """Send turn on command."""
        await self._device.write_gatt(self._char_write, self._model_info["turn_on"])
    
    async def turn_off(self) -> None:
        """Send turn off command."""
        await self._device.write_gatt(self._char_write, self._model_info["turn_off"])