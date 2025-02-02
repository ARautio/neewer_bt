from typing import Optional
import asyncio

from bleak import BleakClient, BleakError

from ..const import MODELS

class NeewerBTDevice:
    """Handle Neewer device."""

    def __init__(self, device, model: str):
        self.state: Optional[bool] = None
        self._device = device
        self._client: Optional[BleakClient] = None
        self._model_info = MODELS[model]
        self._char_write = self._model_info["char_write"]
        self._lock = asyncio.Lock()

    def _include_checksum(self, command: bytes) -> bytes:
        """Include checksum in command.
        Calculates sum of bytes in command and adds it as last byte.
        """
        checksum = sum(command) & 0xFF  # Sum all bytes and take last byte only
        return command + bytes([checksum])
    
    async def turn_on(self) -> None:
        """Send turn on command."""
        """Send turn on command."""
        if self._client is None:
            await self._connect()
        if self._client:  # Type guard
            await self._client.write_gatt_char(
                self._char_write, 
                self._include_checksum(self._model_info["turn_on"]), 
                response=False
            )
            await self._disconnect()
    
    async def turn_off(self) -> None:
        """Send turn off command."""
        if self._client is None:
            await self._connect()
        if self._client:  # Type guard
            await self._client.write_gatt_char(
                self._char_write, 
                self._include_checksum(self._model_info["turn_off"]), 
                response=False
            )
            await self._disconnect()

    async def _connect(self) -> None:
        """Connect to the device."""
        try:
            self._client = BleakClient(self._device)
            await self._client.connect()
        except BleakError as ex:
            self._client = None
            raise ConnectionError from ex
        
    async def _disconnect(self) -> None:
        """Disconnect from the device."""
        await self._client.disconnect()
        self._client = None