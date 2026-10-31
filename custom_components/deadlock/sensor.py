"""Last-match stats as sensors, so they show on the device page and dashboards."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfTime
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN
from .matches import won


@dataclass(frozen=True, kw_only=True)
class StatDescription(SensorEntityDescription):
    value: Callable[[dict], object] | None = None  # defaults to match[key]


STAT = SensorStateClass.MEASUREMENT
SENSORS = (
    StatDescription(
        key="finished",
        name="Last match finished",
        device_class=SensorDeviceClass.TIMESTAMP,  # the UI shows this as "x minutes ago"
        value=lambda m: datetime.fromtimestamp(m["start_time"] + m["match_duration_s"], UTC),
    ),
    StatDescription(
        key="result",
        name="Last match result",
        device_class=SensorDeviceClass.ENUM,
        options=["win", "loss"],
        value=lambda m: "win" if won(m) else "loss",
    ),
    StatDescription(key="player_kills", name="Last match kills", state_class=STAT),
    StatDescription(key="player_deaths", name="Last match deaths", state_class=STAT),
    StatDescription(key="player_assists", name="Last match assists", state_class=STAT),
    StatDescription(key="net_worth", name="Last match net worth", state_class=STAT),
    StatDescription(
        key="match_duration_s",
        name="Last match duration",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=STAT,
        value=lambda m: round(m["match_duration_s"] / 60),
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(LastMatchStat(entry.runtime_data, entry, d) for d in SENSORS)


class LastMatchStat(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, description: StatDescription):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.unique_id)})

    @property
    def native_value(self):
        m = max(self.coordinator.data, key=lambda m: m["match_id"], default=None)
        if m is None:
            return None
        d = self.entity_description
        return d.value(m) if d.value else m.get(d.key)
