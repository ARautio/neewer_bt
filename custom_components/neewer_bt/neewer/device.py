from typing import Optional, List
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

    def _include_checksum(self, command: List[int]) -> List[int]:
        """Include checksum in command.
        Calculates sum of bytes in command and adds it as last byte.
        """
        checksum = sum(command) & 0xFF
        return command + [checksum]

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

    async def _write_command(self, command: List[int]) -> None:
        """Write command to device with connection handling."""
        try:
            await self._connect()
            await self._client.write_gatt_char(
                self._char_write, self._include_checksum(command), response=False
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

    async def set_cct(self, brightness: int, temperature: int, gm: int = 50) -> None:
        """Send CCT command with brightness, temperature and GM compensation.

        brightness: 0-100
        temperature: 32-56 (3200K-5600K)
        gm: 0-100, default centered at 50
        """
        command = [
            120,
            135,
            2,
            max(0, min(100, int(brightness))),
            max(32, min(56, int(temperature))),
            max(0, min(100, int(gm))),
        ]
        await self._write_command(command)
        self.state = True
