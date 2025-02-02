"""Constants for the Neewer integration."""
from typing import Final

from .neewer.const import MODELS

DOMAIN = "neewer_bt"

LOCAL_NAMES = set(MODELS.keys())
MANUFACTURER = "Neewer"

DEVICE_TIMEOUT = 30
UPDATE_SECONDS = 30