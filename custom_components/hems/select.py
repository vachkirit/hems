from homeassistant.components.select import SelectEntity

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


class HEMSModeSelect(SelectEntity):
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
