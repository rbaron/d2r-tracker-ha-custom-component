from custom_components.d2r_tracker.const import ORIGIN_DIABLO2IO
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
import logging


_LOGGER = logging.getLogger(__name__)


def get_diablo2io_api_response(api_key: str | None, contact_email: str) -> dict:
    """Return API response as a dictionary."""
    response = requests.get(
        "https://diablo2.io/dclone_api.php",
        # As per https://diablo2.io/forums/public-api-for-diablo-clone-uber-diablo-tracker-t906872.html
        # No API key is required as of writing.
        # > Timings between API requests from your app should never be less than 60 seconds apart.
        # No headers required, but we add some to identify our app.
        headers={
            "From": "Home Assistant integration github.com/rbaron/d2r-tracker-ha-custom-component",
            "Contact-Email": contact_email,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def group_diablo2io_response(response: dict) -> DCloneProgress:
    entries = defaultdict(lambda: defaultdict(dict))

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
        entries[region][ladder][hardcore] = {  # type: ignore[index]
            "progress": int(entry["progress"]),
            "last_update_timestamp": entry["timestamped"],
        }

    def get_progress(region: str, ladder: bool, hardcore: bool) -> Progress:
        return entries[region][ladder][hardcore]["progress"]

    def make_core(region: str, ladder: bool) -> DCloneCoreProgress:
        return DCloneCoreProgress(
            HC=Progress(get_progress(region, ladder, True)),
            SC=Progress(get_progress(region, ladder, False)),
        )

    def make_region(region: str) -> DCloneLadderProgress:
        return DCloneLadderProgress(
            L=make_core(region, True),
            NL=make_core(region, False),
        )

    return DCloneProgress(
        Americas=make_region("Americas"),
        Europe=make_region("Europe"),
        Asia=make_region("Asia"),
        China=None,  # Not available from diablo2.io.
    )


class Diablo2IOProvider(ProviderBase):
    NAME = ORIGIN_DIABLO2IO

    def __init__(self, api_key: str | None, contact_email: str):
        self.api_key = api_key
        self.contact_email = contact_email

    def get_terror_zone(self) -> TerrorZoneResponse:
        raise NotImplementedError

    def get_dclone_progress(self) -> DCloneProgress:
        return group_diablo2io_response(
            get_diablo2io_api_response(
                self.api_key,
                self.contact_email,
            )
        )

    def get_attribution(self) -> str:
        return "Data courtesy of diablo2.io"
