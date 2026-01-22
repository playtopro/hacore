"""Base class for P2P entities."""

from homeassistant.const import CONF_HOST
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_FIRMWARE, DOMAIN
from .coordinator import P2PDataUpdateCoordinator


class P2PEntity(CoordinatorEntity[P2PDataUpdateCoordinator]):
    """Defines a base P2P entity."""

    def __init__(self, coordinator: P2PDataUpdateCoordinator) -> None:
        """Initialize P2P entity."""
        super().__init__(coordinator)

        if self.coordinator.config_entry is not None:
            conf_host: str = self.coordinator.config_entry.data[CONF_HOST]

            firmware: str = "unknown"

            if self.coordinator.config_entry.data.get(CONF_FIRMWARE):
                firmware = self.coordinator.config_entry.data[CONF_FIRMWARE]

            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, conf_host)},
                model="lichen play",
                manufacturer="playtopro",
                name="lichen play",
                sw_version=firmware,
            )
