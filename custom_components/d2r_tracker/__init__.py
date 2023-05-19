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


def get_d2runewizard_api_response(url: str, api_key: str | None) -> str:
    """Return API response."""
    # headers = {"User-Agent": "Curl"}
    headers = {
        "D2R-Contact": "d2r@rbaron.net",
        "D2R-Platform": "Home Assistant",
        "D2R-Repo": "https://github.com/rbaron/d2r-tracker-ha-custom-component",
    }
    params = {
        "token": api_key,
    }
    response = requests.get(url, timeout=60, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def ensure_bool(val: bool | str) -> bool:
    if isinstance(val, bool):
        return val
    elif isinstance(val, str):
        match val.lower():
            case "true":
                return True
            case "false":
                return False
    raise ValueError(f"Invalid value for bool: {val}")


def group_d2runewizard_response(response: dict):
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
        "provided_by": response["providedBy"],
        "version": response["version"],
    }
    for entry in response["servers"]:
        res["entries"][entry["region"]][ensure_bool(entry["ladder"])][
            ensure_bool(entry["hardcore"])
        ] = {
            "progress": entry["progress"],
            "last_update_timestamp": entry["lastUpdate"]["seconds"],
        }
    return res


class D2RuneWizardClient:
    def __init__(self, api_key: str | None):
        self.api_key = api_key
        self.terrorzone_next_fetch = datetime.now()
        self.last_terrorzone = None

    @cached(cache=TTLCache(maxsize=1, ttl=60))
    def get_dclone_progress(self):
        grouped_response = group_d2runewizard_response(
            get_d2runewizard_api_response(
                "https://d2runewizard.com/api/diablo-clone-progress/all", self.api_key
            )
        )
        return grouped_response

    def get_terrorzone(self):
        now = datetime.now()

        if now < self.terrorzone_next_fetch:
            _LOGGER.debug("Using cached terrorzone: %s", self.last_terrorzone)
            return self.last_terrorzone

        self.last_terrorzone = self._internal_get_terrorzone()
        n_votes = self.last_terrorzone["terror_zone"]["n_votes"]
        if n_votes > 3:
            # Round time to next whole hour.
            self.terrorzone_next_fetch = now.replace(
                minute=0, second=0, microsecond=0
            ) + timedelta(hours=1)
            _LOGGER.debug(
                "Got valid answer. Will fetch next terror zone at: %s",
                self.terrorzone_next_fetch,
            )
        else:
            self.terrorzone_next_fetch = now + timedelta(seconds=60)
            _LOGGER.debug(
                "Got answer with insufficient votes. \
                    Will fetch next terror zone at: %s",
                self.terrorzone_next_fetch,
            )

        return self.last_terrorzone

    @cached(cache=TTLCache(maxsize=1, ttl=60))
    def _internal_get_terrorzone(self):
        res = get_d2runewizard_api_response(
            "https://d2runewizard.com/api/terror-zone", self.api_key
        )
        return {
            "terror_zone": {
                "zone": res["terrorZone"]["highestProbabilityZone"]["zone"],
                "probability": res["terrorZone"]["highestProbabilityZone"][
                    "probability"
                ],
                "n_votes": res["terrorZone"]["highestProbabilityZone"]["amount"],
                "last_updated": dt.utc_from_timestamp(
                    res["terrorZone"]["lastUpdate"]["seconds"]
                ),
            }
        }


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
