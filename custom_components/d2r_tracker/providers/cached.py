from datetime import datetime, timedelta
from typing import Optional

from cachetools import TTLCache, cached
from custom_components.d2r_tracker.providers import (
    DCloneProgress,
    ProviderBase,
    ProviderResponse,
    TerrorZoneResponse,
)

from homeassistant.util import dt
import logging

_LOGGER = logging.getLogger(__name__)


class CachedProvider(ProviderBase):
    def __init__(self, provider: ProviderBase):
        """Initialize cached provider."""
        self.provider = provider

        self.last_terror_zone_response: Optional[TerrorZoneResponse] = None
        self.next_terror_zone_update_after: Optional[datetime] = None

    @property
    def NAME(self) -> str:
        return self.provider.NAME

    def get_attribution(self) -> str:
        return self.provider.get_attribution()

    # Regular 60s TTL'd cache.
    @cached(cache=TTLCache(maxsize=1, ttl=60))
    def get_dclone_progress(self) -> DCloneProgress:
        _LOGGER.debug(
            f"Cache miss for dclone progress, fetching from provider {self.provider.NAME}"
        )
        return self.provider.get_dclone_progress()

    def get_terror_zone(self) -> TerrorZoneResponse:
        if (
            self.next_terror_zone_update_after is not None
            and self.last_terror_zone_response is not None
            and dt.now() < self.next_terror_zone_update_after
        ):
            return self.last_terror_zone_response

        _LOGGER.debug(
            f"Cache miss for terror zone, fetching from provider {self.provider.NAME}"
        )

        self.last_terror_zone_response = self.provider.get_terror_zone()
        now = dt.now()

        # In the first 5 minutes, fetch every minute.
        if now.minute < 5:
            self.next_terror_zone_update_after = now.replace(
                second=0, microsecond=0
            ) + timedelta(minutes=1)
        # Otherwise, schedule fetch for the next whole hour.
        else:
            self.next_terror_zone_update_after = now.replace(
                minute=0, second=0, microsecond=0
            ) + timedelta(hours=1)

        _LOGGER.debug(
            f"Next terror zone update scheduled at {self.next_terror_zone_update_after.isoformat()}"
        )

        return self.last_terror_zone_response

    def collate_responses(self) -> ProviderResponse:
        terror_zone = None
        try:
            terror_zone = self.get_terror_zone()
        except NotImplementedError:
            _LOGGER.debug(f"Terror zone fetching not implemented for: {self.NAME}")
            pass
        dclone_progress = None
        try:
            dclone_progress = self.get_dclone_progress()
        except NotImplementedError:
            _LOGGER.debug(f"DClone progress fetching not implemented for: {self.NAME}")
            pass
        return ProviderResponse(
            terror_zone=terror_zone, dclone_progress=dclone_progress
        )
