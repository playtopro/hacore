"""Constants for the lichen playtopro integration."""

from datetime import timedelta
import logging

DOMAIN = "playtopro"
CONF_SERIAL = "serial"
CONF_FIRMWARE = "firmware"
LOGGER = logging.getLogger(__package__)
SCAN_INTERVAL = timedelta(seconds=10)
