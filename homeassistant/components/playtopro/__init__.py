"""The lichen playtopro integration."""

# To validate the integration, run:
# python3 -m script.hassfest --integration-path ./components/playtopro
# You have to set your target level in your manifest.json.
# To bypass the check so your integration will load, first set:
# "quality_scale":"internal"
# Then, tell home assistant to bypass the check.
# Locate script/hassfest/quality_scale.py
# Locate INTEGRATIONS_WITHOUT_SCALE, and add the domain name - playtopro.
# To confirm, rerun the following can you should get a pass:
# python3 -m script.hassfest --integration-path ./homeassistant/components/playtopro
# Finally, to have your integration included, run:
# python3 -m script.hassfest
# To confirm that your integration in now available, check:
# /workspaces/hacore/homeassistant/generated/config_flows.py
# Your integratioin should appear in the list of integrations.
# If you have imported your files using docker desktop, you need to adjust the
# file permissions to allow the scripts to read the files.
# You can do this by running:
# sudo chown -R vscode ./playtopro
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .coordinator import P2PDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up lichen playtopro from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    entry.runtime_data = P2PDataUpdateCoordinator(hass, entry=entry)
    await entry.runtime_data.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
