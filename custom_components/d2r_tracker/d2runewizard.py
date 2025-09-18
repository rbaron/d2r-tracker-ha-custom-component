from ast import Dict
from typing import Any
import requests
from cachetools import cached, TTLCache
from datetime import datetime, timedelta
from collections import defaultdict
import json

import logging

_LOGGER = logging.getLogger(__name__)
try:
    from homeassistant.util import dt
except ImportError:
    _LOGGER.warning("Home Assistant version is too old, dt module not available.")
    pass


def get_d2runewizard_api_response(
    url: str, api_key: str | None, contact_email: str
) -> dict:
    """Return API response."""
    headers = {
        "D2R-Contact": contact_email,
        "D2R-Platform": "Home Assistant -- github.com/rbaron/d2r-tracker-ha-custom-component",
        "D2R-Repo": "https://github.com/rbaron/d2r-tracker-ha-custom-component",
    }
    params = {
        "token": api_key,
    }
    response = requests.get(url, timeout=60, headers=headers, params=params)
    response.raise_for_status()
    _LOGGER.info(f"Response from {url}: {json.dumps(response.json(), indent=2)}")
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
        _LOGGER.info(f"Processing entry: {json.dumps(entry, indent=2)}")
        res["entries"][entry["region"]][ensure_bool(entry["ladder"])][
            ensure_bool(entry["hardcore"])
        ] = {
            "progress": entry["progress"],
            "last_update_timestamp": entry.get("lastUpdate", dict()).get("seconds", 0),
        }
    return res


class D2RuneWizardClient:
    def __init__(self, api_key: str | None, contact_email: str):
        self.api_key = api_key
        self.terrorzone_next_fetch = datetime.now()
        self.contact_email = contact_email
        self.last_terrorzone = None

    @cached(cache=TTLCache(maxsize=1, ttl=60))
    def get_dclone_progress(self) -> dict:
        grouped_response = group_d2runewizard_response(
            get_d2runewizard_api_response(
                "https://d2runewizard.com/api/diablo-clone-progress/all",
                self.api_key,
                self.contact_email,
            )
        )
        return grouped_response

    def get_terrorzone(self) -> dict:
        now = datetime.now()

        if now < self.terrorzone_next_fetch:
            _LOGGER.debug("Using cached terrorzone: %s", self.last_terrorzone)
            return self.last_terrorzone or {}

        self.last_terrorzone = self._internal_get_terrorzone()
        # Next update: 10 seconds past the hour, capped to 30 minutes from now.
        next_fetch = (now + timedelta(hours=1)).replace(
            minute=0, second=10, microsecond=0
        )
        self.terrorzone_next_fetch = min(next_fetch, now + timedelta(minutes=30))
        _LOGGER.info(
            "Will fetch next terror zone at: %s",
            self.terrorzone_next_fetch,
        )

        return self.last_terrorzone

    @cached(cache=TTLCache(maxsize=1, ttl=60))
    def _internal_get_terrorzone(self):
        res = get_d2runewizard_api_response(
            "https://d2runewizard.com/api/terror-zone", self.api_key, self.contact_email
        )
        return {
            "terror_zone": {
                "zone": res["currentTerrorZone"]["zone"],
                "next": res["nextTerrorZone"]["zone"],
            },
            "last_updated": dt.now(),
        }
