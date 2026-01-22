"""P2P Sensors."""

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import P2PDataUpdateCoordinator
from .entity import P2PEntity
from .P2PDevice import P2PStatusResponse, P2PZone


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up P2P sensor based on a config entry."""
    coordinator = entry.runtime_data

    async_add_entities([P2PEcoModeFactor(coordinator)])
    async_add_entities([P2PZoneSensor(coordinator, index) for index in range(8)])


class P2PEcoModeFactor(P2PEntity, SensorEntity):
    """P2P Sensor."""

    ICON: str = "mdi:water-percent"

    def __init__(self, coordinator: P2PDataUpdateCoordinator) -> None:
        """Initializes the Switch."""
        super().__init__(coordinator)
        # Setup unique ID for this entity
        if self.coordinator.config_entry is not None:
            conf_host: str = self.coordinator.config_entry.data[CONF_HOST]
            self._attr_unique_id = f"{conf_host}_{'eco_mode_factor'}"

    @callback
    def _handle_coordinator_update(self) -> None:
        if self.coordinator.data is not None:
            if self.coordinator.data["status"]:
                status_response: P2PStatusResponse = self.coordinator.data["status"]
                self._attr_native_value = status_response.eco_mode_factor

        self.async_write_ha_state()

    @property
    def name(self) -> str:
        """Get the name."""
        return "Eco Mode Factor"

    @property
    def description(self) -> str:
        """Get the description name."""
        return "Percentage runtime based on weather data"

    @property
    def unit_of_measure(self) -> str:
        """Get the unit of Measure."""
        return PERCENTAGE

    @property
    def icon(self) -> str | None:
        """Icon to use in the frontend, if any."""
        return self.ICON


class P2PZoneSensor(P2PEntity, SensorEntity):
    """P2P Sensor."""

    ICON: str = "mdi:sprinkler"
    index: int

    def __init__(self, coordinator: P2PDataUpdateCoordinator, index: int) -> None:
        """Initializes the Switch."""
        super().__init__(coordinator)
        # Setup unique ID for this entity
        if self.coordinator.config_entry is not None:
            conf_host: str = self.coordinator.config_entry.data[CONF_HOST]
            self._attr_unique_id = f"{conf_host}_{'zone'}_{index:02d}"

        self.index = index

    @callback
    def _handle_coordinator_update(self) -> None:
        if self.coordinator.data is not None:
            if self.coordinator.data["status"]:
                status_response: P2PStatusResponse = self.coordinator.data["status"]
                zone: P2PZone = status_response.zones[self.index]
                self._attr_native_value = zone.on

        self.async_write_ha_state()

    @property
    def name(self) -> str:
        """Get the name."""
        return f"{'Zone '}{(self.index + 1):02d}"

    @property
    def description(self) -> str:
        """Get the description name."""
        return f"{'ON/Off status of '}{self.name}"

    @property
    def unit_of_measure(self) -> str:
        """Get the unit of Measure."""
        return PERCENTAGE

    @property
    def icon(self) -> str | None:
        """Icon to use in the frontend, if any."""
        return self.ICON

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""

        result: dict[str, Any] = {}

        if self.coordinator.data is not None:
            if self.coordinator.data["status"]:
                status_response: P2PStatusResponse = self.coordinator.data["status"]
                zone: P2PZone = status_response.zones[self.index]
                result = {
                    "manual_mode_active": zone.manual_mode_active,
                    "eco_mode_active": zone.eco_mode_active,
                    # "sleep_mode_active": zone.sleep_mode_active,
                }
        return result
