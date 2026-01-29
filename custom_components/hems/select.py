from homeassistant.components.select import SelectEntity
from homeassistant.helpers.restore_state import RestoreEntity

from .engine.const import MODE_NORMAL, MODE_ECO, MODE_RECHARGE
from . import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup du select HEMS via config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    engine = data["engine"]
    coordinator = data["coordinator"]

    async_add_entities([
        HEMSModeSelect(engine, coordinator)
    ])


class HEMSModeSelect(SelectEntity, RestoreEntity):
    _attr_name = "HEMS Mode"
    _attr_icon = "mdi:transmission-tower"
    _attr_should_poll = False

    def __init__(self, engine, coordinator):
        self.engine = engine
        self.coordinator = coordinator

        self._attr_options = [
            MODE_NORMAL,
            MODE_ECO,
            MODE_RECHARGE,
        ]

    @property
    def current_option(self):
        return self.engine.context.mode

    async def async_select_option(self, option: str):
        self.engine.context.mode = option
        self.engine.update()
        self.coordinator._notify_sensors()

    async def async_added_to_hass(self):
        """Restore last selected mode."""
        last_state = await self.async_get_last_state()
        if last_state and last_state.state in self._attr_options:
            self.engine.context.mode = last_state.state

