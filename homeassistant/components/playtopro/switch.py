"""P2P Irrigation Switches."""

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
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
    """Set up P2P switch based on a config entry."""
    coordinator = entry.runtime_data

    async_add_entities([P2PZoneManualMode(coordinator, index) for index in range(8)])
    async_add_entities([P2PAutoMode(coordinator)])
    async_add_entities([P2PZoneAutoMode(coordinator, index) for index in range(8)])
    async_add_entities([P2PEcoMode(coordinator)])
    async_add_entities([P2PZoneEcoMode(coordinator, index) for index in range(8)])
    async_add_entities([P2PZoneSleepMode(coordinator, index) for index in range(8)])


class P2PZoneManualMode(P2PEntity, SwitchEntity):
    """P2P Zone manual mode."""

    ICON: str = "mdi:run"
    index: int

    def __init__(self, coordinator: P2PDataUpdateCoordinator, index: int) -> None:
        """Initializes the Switch."""
        super().__init__(coordinator)
        # Setup unique ID for this entity
        if self.coordinator.config_entry is not None:
            conf_host: str = self.coordinator.config_entry.data[CONF_HOST]
            self._attr_unique_id = f"{conf_host}_{'zone_manual_mode'}_{index:02d}"

        self.index = index

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()

    @property
    def name(self) -> str:
        """Get the name."""
        return f"{'Zone '}{(self.index + 1):02d}{' Manual Mode'}"

    @property
    def description(self) -> str:
        """Get the description name."""
        return f"{'Manual mode '}{self.name}"

    @property
    def is_on(self) -> bool | None:
        """Return true if device is on."""
        if self.coordinator.data is not None:
            status_response: P2PStatusResponse = self.coordinator.data["status"]
            zone: P2PZone = status_response.zones[self.index]
            return zone.manual_mode_active
        return None

    @property
    def icon(self) -> str | None:
        """Icon to use in the frontend."""
        return self.ICON

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn zone on."""
        await self.coordinator.async_set_zone_manual_mode(self.index, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn zone off."""
        await self.coordinator.async_set_zone_manual_mode(self.index, False)


class P2PAutoMode(P2PEntity, SwitchEntity):
    """P2P auto mode."""

    ICON: str = "mdi:checkbox-marked-circle-auto-outline"

    def __init__(self, coordinator: P2PDataUpdateCoordinator) -> None:
        """Initializes the Switch."""
        super().__init__(coordinator)
        # Setup unique ID for this entity
        if self.coordinator.config_entry is not None:
            conf_host: str = self.coordinator.config_entry.data[CONF_HOST]
            self._attr_unique_id = f"{conf_host}_{'auto_mode'}"

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()

    @property
    def name(self) -> str:
        """Get the name."""
        return "Auto Mode"

    @property
    def description(self) -> str:
        """Get the description name."""
        return "Run the devices own scheduled"

    @property
    def is_on(self) -> bool | None:
        """Return true if device is configured to run it's internal schedule."""
        if self.coordinator.data is not None:
            if self.coordinator.data["status"]:
                status_response: P2PStatusResponse = self.coordinator.data["status"]
                return status_response.system_auto
        return None

    @property
    def icon(self) -> str | None:
        """Icon to use in the frontend."""
        return self.ICON

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable auto mode."""
        await self.coordinator.async_set_auto_mode(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable auto mode."""
        await self.coordinator.async_set_auto_mode(False)


class P2PZoneAutoMode(P2PEntity, SwitchEntity):
    """P2P Zone auto mode."""

    ICON: str = "mdi:checkbox-marked-circle-auto-outline"
    index: int

    def __init__(self, coordinator, index: int) -> None:
        """Initializes the Switch."""
        super().__init__(coordinator)
        # Setup unique ID for this entity
        if self.coordinator.config_entry is not None:
            conf_host: str = self.coordinator.config_entry.data[CONF_HOST]
            self._attr_unique_id = f"{conf_host}_{'zone_auto_mode'}_{index:02d}"
        self.index = index

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()

    @property
    def name(self) -> str:
        """Get the name."""
        return f"{'Zone '}{(self.index + 1):02d}{' Auto Mode'}"

    @property
    def description(self) -> str:
        """Get the description name."""
        return f"{'Auto mode'}{self.name}"

    @property
    def is_on(self) -> bool | None:
        """Return true if device is on."""
        if self.coordinator.data is not None:
            if self.coordinator.data["status"]:
                status_response: P2PStatusResponse = self.coordinator.data["status"]
                return status_response.zones[self.index].auto_mode
        return None

    @property
    def icon(self) -> str | None:
        """Icon to use in the frontend."""
        return self.ICON

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable zone auto mode."""
        await self.coordinator.async_set_zone_auto_mode(self.index, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable zone auto mode."""
        await self.coordinator.async_set_zone_auto_mode(self.index, False)


class P2PEcoMode(P2PEntity, SwitchEntity):
    """P2P eco mode."""

    ICON: str = "mdi:leaf"

    def __init__(self, coordinator) -> None:
        """Initializes the Switch."""
        super().__init__(coordinator)
        # Setup unique ID for this entity
        if self.coordinator.config_entry is not None:
            conf_host: str = self.coordinator.config_entry.data[CONF_HOST]
            self._attr_unique_id = f"{conf_host}_{'eco_mode'}"

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()

    @property
    def name(self) -> str:
        """Get the name."""
        return "Eco Mode"

    @property
    def description(self) -> str:
        """Get the description name."""
        return "Run the devices own scheduled"

    @property
    def is_on(self) -> bool | None:
        """Return true if device eco mode is on."""
        if self.coordinator.data is not None:
            if self.coordinator.data["status"]:
                status_response: P2PStatusResponse = self.coordinator.data["status"]
                return status_response.eco_mode
        return None

    @property
    def icon(self) -> str | None:
        """Icon to use in the frontend."""
        return self.ICON

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable eco mode."""
        await self.coordinator.async_set_eco_mode(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable eco mode."""
        p2p_coordinator: P2PDataUpdateCoordinator = self.coordinator
        await p2p_coordinator.async_set_eco_mode(False)


class P2PZoneEcoMode(P2PEntity, SwitchEntity):
    """P2P Zone eco mode."""

    ICON: str = "mdi:leaf"
    index: int

    def __init__(self, coordinator, index: int) -> None:
        """Initializes the Switch."""
        super().__init__(coordinator)
        # Setup unique ID for this entity
        if self.coordinator.config_entry is not None:
            conf_host: str = self.coordinator.config_entry.data[CONF_HOST]
            self._attr_unique_id = f"{conf_host}_{'zone_eco_mode'}_{index:02d}"
            self.index = index

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()

    @property
    def name(self) -> str:
        """Get the name."""
        return f"{'Zone '}{(self.index + 1):02d}{' Eco Mode'}"

    @property
    def description(self) -> str:
        """Get the description name."""
        return f"{'Eco mode'}{self.name}"

    @property
    def is_on(self) -> bool | None:
        """Return true if zone eco mode is on."""
        if self.coordinator.data is not None:
            if self.coordinator.data["status"]:
                status_response: P2PStatusResponse = self.coordinator.data["status"]
                return status_response.zones[self.index].eco_mode
        return None

    @property
    def icon(self) -> str | None:
        """Icon to use in the frontend."""
        return self.ICON

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable zone eco mode."""
        result: bool = await self.coordinator.async_set_zone_eco_mode(self.index, True)

        if result:
            self._attr_is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable zone eco mode."""
        result: bool = await self.coordinator.async_set_zone_eco_mode(self.index, False)

        if result:
            self._attr_is_on = False
            self.async_write_ha_state()


class P2PZoneSleepMode(P2PEntity, SwitchEntity):
    """P2P Zone sleep mode."""

    ICON: str = "mdi:sleep"
    index: int

    def __init__(self, coordinator, index: int) -> None:
        """Initializes the Switch."""
        super().__init__(coordinator)
        # Setup unique ID for this entity
        if self.coordinator.config_entry is not None:
            conf_host: str = self.coordinator.config_entry.data[CONF_HOST]
            self._attr_unique_id = f"{conf_host}_{'zone_sleep_mode'}_{index:02d}"
            self.index = index

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()

    @property
    def name(self) -> str:
        """Get the name."""
        return f"{'Zone '}{(self.index + 1):02d}{' Sleep Mode'}"

    @property
    def description(self) -> str:
        """Get the description name."""
        return f"{'Sleep mode'}{self.name}"

    @property
    def is_on(self) -> bool | None:
        """Return true if zone sleep mode is on."""
        if self.coordinator.data is not None:
            if self.coordinator.data["status"]:
                status_response: P2PStatusResponse = self.coordinator.data["status"]
                return status_response.zones[self.index].sleep_mode
        return None

    @property
    def icon(self) -> str | None:
        """Icon to use in the frontend."""
        return self.ICON

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable zone sleep mode."""
        result: bool = await self.coordinator.async_set_zone_sleep_mode(
            self.index, True
        )

        if result:
            self._attr_is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable zone sleep mode."""
        result: bool = await self.coordinator.async_set_zone_sleep_mode(
            self.index, False
        )

        if result:
            self._attr_is_on = False
            self.async_write_ha_state()
