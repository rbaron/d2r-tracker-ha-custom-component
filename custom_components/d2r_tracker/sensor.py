"""D2R sensor integration."""
from __future__ import annotations

import itertools

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import D2RDataUpdateCoordinator
from .const import DOMAIN

REGIONS = [
    "Americas",
    "Asia",
    "Europe",
]


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

    origin = config_entry.data["origin"]

    assert device_id is not None

    entities: list[SensorEntity] = [
        D2RDiabloCloneTracker(coordinator, device_id, origin, region, ladder, hardcore)
        for (region, ladder, hardcore) in itertools.product(
            REGIONS, [True, False], [True, False]
        )
    ]

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
        self._attr_name = f"D2R {sensor_type}"
        self._attr_unique_id = f"{sensor_type}-{device_id}"

    @property
    def device_info(self):
        """Device info."""
        return self.coordinator.device_info


class D2RDiabloCloneTracker(D2RSensorBase):
    """D2R Diablo Clone Tracker for one region/ladder/hardcore config."""

    _attr_icon = "mdi:poll"
    origin: str
    region: str
    ladder: bool
    hardcore: bool

    def __init__(
        self,
        coordinator: D2RDataUpdateCoordinator,
        device_id: str,
        origin: str,
        region: str,
        ladder: bool,
        hardcore: bool,
    ) -> None:
        """Initialize a new D2RDiabloCloneTracker sensor."""
        super().__init__(
            coordinator,
            f"{origin} {region} {'HC' if hardcore else 'SC'} {'L' if ladder else 'NL'}",
            device_id,
        )
        self.region = region
        self.ladder = ladder
        self.hardcore = hardcore

    @property
    def native_value(self):
        """Return sensor state."""
        data = self.coordinator.data
        progress = data["entries"][self.region][self.ladder][self.hardcore]["progress"]
        return f"{progress}/6"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data
