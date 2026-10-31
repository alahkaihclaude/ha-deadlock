from homeassistant.components.event import EventEntity
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN
from .matches import new_matches, won

ATTRS = ("match_id", "hero_id", "player_kills", "player_deaths", "player_assists", "net_worth", "match_duration_s")


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([MatchResult(entry.runtime_data, entry)])


class MatchResult(CoordinatorEntity, EventEntity):
    _attr_has_entity_name = True
    _attr_name = "Match result"
    _attr_event_types = ["win", "loss"]

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.unique_id}_match_result"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id)}, name=entry.title, manufacturer="Deadlock API"
        )
        # shortcut: starts from the newest match at startup, so games finished while HA was down never fire; persist last_id if that matters
        self._last_match = max(coordinator.data, key=lambda m: m["match_id"], default=None)
        self._last_id = self._last_match["match_id"] if self._last_match else 0

    @property
    def extra_state_attributes(self):
        """The newest match's stats, shown even before the first event so the UI can offer them."""
        m = self._last_match
        return m and {"result": "win" if won(m) else "loss", **{k: m.get(k) for k in ATTRS}}

    @callback
    def _handle_coordinator_update(self) -> None:
        for match in new_matches(self.coordinator.data, self._last_id):
            self._last_match = match  # before writing, so the stats match the event that fires
            self._trigger_event("win" if won(match) else "loss", {k: match.get(k) for k in ATTRS})
            self._last_id = match["match_id"]
            self.async_write_ha_state()  # once per match, so two games in one poll fire two automations
