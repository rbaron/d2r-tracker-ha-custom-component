from custom_components.d2r_tracker.const import ORIGIN_D2RUNEWIZARD
from custom_components.d2r_tracker.providers import (
    DCloneCoreProgress,
    DCloneLadderProgress,
    Progress,
    DCloneProgress,
    ProviderBase,
    TerrorZoneResponse,
)

import requests
from collections import defaultdict
from homeassistant.util import dt
import logging


_LOGGER = logging.getLogger(__name__)


def get_d2runewizard_api_response(
    url: str, api_key: str | None, contact_email: str
) -> dict:
    """Return API response."""
    # https://d2runewizard.com/integration
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


def group_dclone_response(response: dict) -> DCloneProgress:
    entries = defaultdict(lambda: defaultdict(dict))
    for entry in response["servers"]:
        entries[entry["region"]][ensure_bool(entry["ladder"])][
            ensure_bool(entry["hardcore"])
        ] = {
            "progress": entry["progress"],
            "last_update_timestamp": entry.get("lastUpdate", dict()).get("seconds", 0),
        }

    def get_progress(region, ladder, hardcore):
        return Progress(
            entries[region][ladder].get(
                hardcore, {"progress": 0, "last_update_timestamp": 0}
            )["progress"]
        )

    def make_core(region, ladder):
        return DCloneCoreProgress(
            SC=get_progress(region, ladder, False),
            HC=get_progress(region, ladder, True),
        )

    def make_ladder(region):
        return DCloneLadderProgress(
            L=make_core(region, True),
            NL=make_core(region, False),
        )

    return DCloneProgress(
        Americas=make_ladder("Americas"),
        Europe=make_ladder("Europe"),
        Asia=make_ladder("Asia"),
        China=None,  # Not provided by d2runewizard as of writing.
    )


class D2RuneWizardProvider(ProviderBase):
    NAME = ORIGIN_D2RUNEWIZARD

    def __init__(self, api_key: str, contact_email: str):
        self.api_key = api_key
        self.contact_email = contact_email

    def get_terror_zone(self) -> TerrorZoneResponse:
        res = get_d2runewizard_api_response(
            "https://d2runewizard.com/api/terror-zone", self.api_key, self.contact_email
        )
        return TerrorZoneResponse(
            current=res["currentTerrorZone"]["zone"],
            next=res["nextTerrorZone"]["zone"],
            updated_at=dt.now(),
        )

    def get_dclone_progress(self) -> DCloneProgress:
        grouped_response = group_dclone_response(
            get_d2runewizard_api_response(
                "https://d2runewizard.com/api/diablo-clone-progress/all",
                self.api_key,
                self.contact_email,
            )
        )
        return grouped_response

    def get_attribution(self) -> str:
        return "Data courtesy of d2runewizard.com"
