from typing import TYPE_CHECKING, Optional

from bleak import BleakClient, BleakError
from bleak_retry_connector import establish_connection

from ..const import MODELS

class NeewerBTDevice:
    """Handle Neewer device."""

    def __init__(self, device, model: str):
        self.state: Optional[bool] = None
        self._device = device
        self._client = BleakClient | None
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
        if self._client is None:
            await self._connect()
        await self._client.write_gatt_char(self._char_write, self._include_checksum(self._model_info["turn_on"]), False)
        await self._disconnect()
    
    async def turn_off(self) -> None:
        """Send turn off command."""
        if self._client is None:
            await self._connect()
        await self._client.write_gatt_char(self._char_write, self._include_checksum(self._model_info["turn_off"]), False)
        await self._disconnect()

    async def _connect(self) -> None:
        """Connect to the device."""
        try:
            self._client = await establish_connection(self._device)
        except BleakError as ex:
            raise ConnectionError from ex
        
    async def _disconnect(self) -> None:
        """Disconnect from the device."""
        await self._client.disconnect()
        self._client = None