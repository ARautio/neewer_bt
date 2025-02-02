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
        command_bytes = bytes(command)  # Convert list to bytes
        checksum = sum(command_bytes) & 0xFF
        return command_bytes + bytes([checksum])
    
    async def _connect(self) -> None:
        """Connect to the device."""
        async with self._lock:
            try:
                if not self._client or not self._client.is_connected:
                    self._client = BleakClient(self._device.address)
                    await self._client.connect()
            except BleakError as ex:
                self._client = None
                raise ConnectionError(f"Failed to connect: {ex}") from ex

    async def _write_command(self, command: bytes) -> None:
        """Write command to device with connection handling."""
        try:
            await self._connect()
            await self._client.write_gatt_char(
                self._char_write,
                self._include_checksum(command),
                response=False
            )
        finally:
            if self._client and self._client.is_connected:
                await self._client.disconnect()
                self._client = None

    async def turn_on(self) -> None:
        """Send turn on command."""
        await self._write_command(self._model_info["turn_on"])
        self.state = True

    async def turn_off(self) -> None:
        """Send turn off command."""
        await self._write_command(self._model_info["turn_off"])
        self.state = False
