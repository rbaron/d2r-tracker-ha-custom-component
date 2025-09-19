"""The Diablo 2 Resurrected integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from custom_components.d2r_tracker.providers import ProviderBase, ProviderResponse
from custom_components.d2r_tracker.providers.cached import CachedProvider
from custom_components.d2r_tracker.providers.d2runewizard import D2RuneWizardProvider
from custom_components.d2r_tracker.providers.diablo2io import Diablo2IOProvider

from .const import (
    CONF_CONTACT_EMAIL,
    CONF_ORIGIN,
    DOMAIN,
    ORIGIN_D2RUNEWIZARD,
    ORIGIN_DIABLO2IO,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Diablo 2 Resurrected from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    coordinator = D2RDataUpdateCoordinator(hass, entry, interval=60)

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


def cached_provider_factory(
    origin: str, api_key: str | None, contact_email: str
) -> CachedProvider:
    """Return provider based on origin."""

    def make_raw_provider() -> ProviderBase:
        if origin == ORIGIN_DIABLO2IO:
            return Diablo2IOProvider(api_key, contact_email)
        elif origin == ORIGIN_D2RUNEWIZARD:
            if not api_key:
                raise ValueError(f"API key is required for {origin}")
            return D2RuneWizardProvider(api_key, contact_email)
        raise ValueError(f"Invalid origin: {origin}")

    return CachedProvider(make_raw_provider())


class D2RDataUpdateCoordinator(DataUpdateCoordinator[ProviderResponse]):
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
        self.data = ProviderResponse(terror_zone=None, dclone_progress=None)
        self.cached_provider: CachedProvider = cached_provider_factory(
            config_entry.data[CONF_ORIGIN],
            config_entry.data.get(CONF_API_KEY),
            config_entry.data[CONF_CONTACT_EMAIL],
        )

    async def _async_update_data(self) -> ProviderResponse:
        return await self.hass.async_add_executor_job(
            self.cached_provider.collate_responses
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Device info."""
        origin = self.config_entry.data[CONF_ORIGIN]
        return DeviceInfo(
            identifiers={(DOMAIN, str(self.config_entry.unique_id))},
            manufacturer=self.cached_provider.get_attribution(),
            name=origin,
        )
