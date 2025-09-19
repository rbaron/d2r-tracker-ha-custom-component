"""D2R sensor integration."""

from __future__ import annotations

import itertools
import logging

from homeassistant.components.sensor import SensorEntity, const as sensor_const
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.d2r_tracker.providers import (
    HC,
    LADDER,
    REGIONS,
)

from . import D2RDataUpdateCoordinator
from .const import CONF_ORIGIN, DOMAIN, ORIGIN_D2RUNEWIZARD

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors."""
    device_id = config_entry.unique_id
    coordinator: D2RDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id][
        "coordinator"
    ]

    origin = config_entry.data[CONF_ORIGIN]

    assert device_id is not None

    entities: list[SensorEntity] = [
        D2RDiabloCloneTracker(coordinator, device_id, region, ladder, hardcore)
        for (region, ladder, hardcore) in itertools.product(REGIONS, LADDER, HC)
    ]

    if origin == ORIGIN_D2RUNEWIZARD:
        entities.extend(
            [
                D2RTerrorZoneTracker(coordinator, device_id),
                D2RNextTerrorZoneTracker(coordinator, device_id),
                D2RTerrorZoneLastUpdatedSensor(coordinator, device_id),
            ]
        )

    async_add_entities(entities)


class D2RSensorBase(CoordinatorEntity[D2RDataUpdateCoordinator], SensorEntity):
    """Base D2R Sensor class."""

    def __init__(
        self,
        coordinator: D2RDataUpdateCoordinator,
        sensor_type: str,
        device_id: str,
    ) -> None:
        """Initialize a new D2R sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_name = f"{sensor_type}"
        self._attr_unique_id = f"{sensor_type}-{device_id}"

    @property
    def device_info(self):
        """Device info."""
        return self.coordinator.device_info

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success and self.coordinator.data is not None
        )


class D2RDiabloCloneTracker(D2RSensorBase):
    """D2R Diablo Clone Tracker for one region/ladder/hardcore config."""

    _attr_icon = "mdi:poll"

    def __init__(
        self,
        coordinator: D2RDataUpdateCoordinator,
        device_id: str,
        region: str,
        ladder: str,
        hardcore: str,
    ) -> None:
        """Initialize a new D2RDiabloCloneTracker sensor."""
        super().__init__(
            coordinator,
            f"DClone {region} {ladder} {hardcore}",
            device_id,
        )
        self.region = region
        self.ladder = ladder
        self.hardcore = hardcore

    @property
    def native_value(self):
        """Return sensor state."""
        dclone_progress = self.coordinator.data.dclone_progress
        if dclone_progress is None:
            return None

        try:
            progress = getattr(
                getattr(getattr(dclone_progress, self.region), self.ladder),
                self.hardcore,
            )
            return progress
        # Possibly provider does not have data for this region/ladder/hardcore combo.
        except AttributeError:
            _LOGGER.debug(
                "AttributeError in %s: region: %s, ladder: %s, hardcore: %s",
                dclone_progress,
                self.region,
                self.ladder,
                self.hardcore,
            )


class D2RTerrorZoneTracker(D2RSensorBase):
    """D2R Terror Zone tracker."""

    _attr_icon = "mdi:map"

    def __init__(
        self,
        coordinator: D2RDataUpdateCoordinator,
        device_id: str,
    ) -> None:
        """Initialize a new D2RDiabloCloneTracker sensor."""
        super().__init__(
            coordinator,
            "Terror Zone",
            device_id,
        )

    @property
    def native_value(self):
        """Return sensor state."""
        terror_zone = self.coordinator.data.terror_zone
        if terror_zone is None:
            return None
        return terror_zone.current


class D2RNextTerrorZoneTracker(D2RSensorBase):
    """D2R Terror Zone tracker."""

    _attr_icon = "mdi:map"

    def __init__(
        self,
        coordinator: D2RDataUpdateCoordinator,
        device_id: str,
    ) -> None:
        """Initialize a new D2RNextTerrorZoneTracker sensor."""
        super().__init__(
            coordinator,
            "Next Terror Zone",
            device_id,
        )

    @property
    def native_value(self):
        """Return sensor state."""
        terror_zone = self.coordinator.data.terror_zone
        if terror_zone is None:
            return None
        return terror_zone.next


class D2RTerrorZoneLastUpdatedSensor(D2RSensorBase):
    """D2R Terror Zone Last Updated Sensor."""

    _attr_device_class = sensor_const.SensorDeviceClass.TIMESTAMP
    _attr_name = "Terror Zone Last Updated"

    def __init__(
        self,
        coordinator: D2RDataUpdateCoordinator,
        device_id: str,
    ) -> None:
        """Initialize a new D2RDiabloCloneTracker sensor."""
        super().__init__(
            coordinator,
            "Terror Zone Last Updated",
            device_id,
        )

    @property
    def native_value(self):
        """Return sensor state."""
        terror_zone = self.coordinator.data.terror_zone
        if terror_zone is None:
            return None
        return terror_zone.updated_at
