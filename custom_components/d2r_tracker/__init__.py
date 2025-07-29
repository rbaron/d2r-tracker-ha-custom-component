"""The Diablo 2 Resurrected integration."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
import logging

from cachetools import cached, TTLCache

import requests

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt

from .const import DOMAIN, ORIGIN_D2RUNEWIZARD, ORIGIN_DIABLO2IO
from .d2runewizard import D2RuneWizardClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Diablo 2 Resurrected from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    coordinator = D2RDataUpdateCoordinator(hass, entry, 120)

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


def get_diablo2io_api_response(api_key: str | None) -> str:
    """Return API response."""
    response = requests.get(
        "https://diablo2.io/dclone_api.php",
        headers={"User-Agent": "Curl"},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def group_diablo2_response(response: dict):
    """Return grouped respoonse.

      Example: {
        entries: {
            [region: str]: {
                [ladder: bool]: {
                    [hardcore: bool] = {
                        "progress": int,
                        "last_update_timestamp": int,
                    },
                },
            },
        },
        provided_by: str,
        version: str,
    }.
    """
    res = {
        "entries": defaultdict(lambda: defaultdict(dict)),
        "provided_by": "diablo2.io",
        "version": "?",
    }

    bool_map = {
        "1": True,
        "2": False,
    }

    def get_region(region: str) -> str:
        region_map = {
            "1": "Americas",
            "2": "Europe",
            "3": "Asia",
        }
        return region_map[region]

    for entry in response:
        region: str = get_region(entry["region"])
        ladder: bool = bool_map[entry["ladder"]]
        hardcore: bool = bool_map[entry["hc"]]
        res["entries"][region][ladder][hardcore] = {  # type: ignore[index]
            "progress": int(entry["progress"]),
            "last_update_timestamp": entry["timestamped"],
        }
    return res


class D2RDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching D2R data."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        interval: int,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"d2r-{config_entry.entry_id}",
            update_interval=timedelta(seconds=interval),
        )
        self.hass = hass
        self.config_entry = config_entry
        self.data = {}
        self.origin = config_entry.data["origin"]
        if self.origin == ORIGIN_D2RUNEWIZARD:
            self.client = D2RuneWizardClient(config_entry.data.get(CONF_API_KEY))

    async def _async_update_data(self):
        """Update data via API."""
        origin = self.config_entry.data["origin"]
        api_key = self.config_entry.data.get(CONF_API_KEY)
        try:
            if origin == ORIGIN_DIABLO2IO:
                return group_diablo2_response(
                    await self.hass.async_add_executor_job(
                        get_diablo2io_api_response, api_key
                    )
                )
            if origin == ORIGIN_D2RUNEWIZARD:
                res = await self.hass.async_add_executor_job(
                    self.client.get_dclone_progress
                )
                res.update(
                    await self.hass.async_add_executor_job(self.client.get_terrorzone)
                )
                return res
            raise RuntimeError(f"Invalid origin: {origin}")
        except requests.HTTPError as err:
            raise UpdateFailed(f"Error fetching from {origin}: {err}") from err

    @property
    def device_info(self) -> DeviceInfo:
        """Device info."""
        origin = self.config_entry.data["origin"]
        return DeviceInfo(
            identifiers={(DOMAIN, str(self.config_entry.unique_id))},
            manufacturer=origin,
            name=origin,
        )
