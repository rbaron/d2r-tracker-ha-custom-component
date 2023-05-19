"""Config flow for Diablo 2 Resurrected integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import selector

from .const import DOMAIN, ORIGIN_D2RUNEWIZARD, ORIGIN_DIABLO2IO

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        "origin": selector(
            {"select": {"options": [ORIGIN_DIABLO2IO, ORIGIN_D2RUNEWIZARD]}}
        ),
        vol.Optional(CONF_API_KEY): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    if "origin" not in data:
        raise InvalidOrigin
    elif data["origin"] == ORIGIN_D2RUNEWIZARD and not data.get(CONF_API_KEY):
        raise MissingAPIKey

    return {
        "title": f"{data['origin']}",
        "api_key": data.get("api_key"),
        "origin": data["origin"],
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Diablo 2 Resurrected."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except InvalidOrigin:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(f"d2r-{user_input['origin']}")
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class InvalidOrigin(HomeAssistantError):
    """Error to indicate there is an invalid origin."""


class MissingAPIKey(HomeAssistantError):
    """Error to indicate the API key is missing"""
