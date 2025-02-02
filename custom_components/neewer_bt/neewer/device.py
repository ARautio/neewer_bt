from typing import TYPE_CHECKING, Optional

from ..const import MODELS

class NeewerBTDevice:
    """Handle Neewer device."""

    def __init__(self, device, model: str):
        self.state: Optional[bool] = None
        self._device = device
        self._model_info = MODELS[model]
        self._char_write = self._model_info["char_write"]

    def _include_checksum(self, command: bytes) -> bytes:
        """Include checksum in command.
        Calculates sum of bytes in command and adds it as last byte.
        """
        checksum = sum(command) & 0xFF  # Sum all bytes and take last byte only
        return command + bytes([checksum])
    
    async def turn_on(self) -> None:
        """Send turn on command."""
        await self._device.write_gatt(self._char_write, self._include_checksum(self._model_info["turn_on"]), False)
    
    async def turn_off(self) -> None:
        """Send turn off command."""
        await self._device.write_gatt(self._char_write, self._include_checksum(self._model_info["turn_off"]), False)