"""Config flow for the lichen playtopro integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util.network import is_ip_address

from .const import CONF_FIRMWARE, CONF_SERIAL, DOMAIN
from .P2PDevice import P2PDevice, P2PError, P2PFirmwareResponse

_LOGGER = logging.getLogger(__name__)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=1233): int,
        vol.Required(CONF_SERIAL): int,
    }
)


class P2PConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for lichen playtopro."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> P2POptionsFlowHandler:
        """Get the options flow for this handler."""
        return P2POptionsFlowHandler()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        # if the user has provided input
        if user_input is not None:
            # if the host is a valid IP address
            if is_ip_address(user_input[CONF_HOST]):
                # Make sure that the host has not already been configured
                entry: ConfigEntry | None = (
                    self.hass.config_entries.async_entry_for_domain_unique_id(
                        DOMAIN, user_input[CONF_HOST]
                    )
                )

                if not entry:
                    # Setup Lichen hub to connect to the device
                    hub: P2PDevice = P2PDevice(
                        ipv4=user_input[CONF_HOST],
                        serial_number=user_input[CONF_SERIAL],
                    )

                    try:
                        # Attempt to connect to Device and get status
                        firmwareResponse: P2PFirmwareResponse = (
                            await hub.async_get_firmware()
                        )

                        # Confirm device firmware is supported
                        if firmwareResponse.firmware >= 26:
                            # Now check that the private key is correct
                            # Status requires a correct private key
                            await hub.async_get_status()

                            # Save user input as a valid device
                            await self.async_set_unique_id(user_input[CONF_HOST])

                            # Append the firmware version to the input
                            user_input = {
                                CONF_FIRMWARE: firmwareResponse.firmware,
                                **user_input,
                            }

                            return self.async_create_entry(
                                title=user_input[CONF_HOST],
                                data=user_input,
                            )
                        errors["base"] = "firmware_not_supported"
                    except ConnectionError:
                        errors["base"] = "cannot_connect"
                    except P2PError as err:
                        errors["base"] = err.error
                else:
                    errors["base"] = "already_configured_device"
            else:
                errors["base"] = "invalid_ip_address"

            # Show the form again, keeping the users input
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_HOST, default=user_input[CONF_HOST]): str,
                        vol.Required(CONF_PORT, default=user_input[CONF_PORT]): int,
                        vol.Required(CONF_SERIAL, default=user_input[CONF_SERIAL]): int,
                    }
                ),
                errors=errors,
            )
        return self.async_show_form(
            step_id="user", data_schema=OPTIONS_SCHEMA, errors=errors
        )


class P2POptionsFlowHandler(OptionsFlow):
    """Handle P2P options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage P2P options."""
        if user_input is not None:
            # Manually update & reload the config entry after options change.
            changed: bool = self.hass.config_entries.async_update_entry(
                entry=self.config_entry,
                # Since the host is not included as a configurable option
                # we have to append it to the user_input and pass the entire
                # data structure for the entity
                data={CONF_HOST: self.config_entry.data[CONF_HOST], **user_input},
            )
            if changed:
                await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            # Load in the current configuration and setup and validation
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_PORT, default=self.config_entry.data[CONF_PORT]
                    ): int,
                    vol.Required(
                        CONF_SERIAL, default=self.config_entry.data[CONF_SERIAL]
                    ): int,
                }
            ),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
