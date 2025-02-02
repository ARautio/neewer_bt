"""Constants for the Neewer integration."""
from typing import Final

from .neewer.const import MODELS

DOMAIN = "NEEWER_BT"

LOCAL_NAMES = set(MODELS.keys())
MANUFACTURER = "Neewer"

DEVICE_TIMEOUT = 30
