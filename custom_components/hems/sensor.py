from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    engine = data["engine"]
    coordinator = data["coordinator"]

    sensors = [
        HEMSConsigneSensor(inv)
        for inv in engine.context.inverters
    ]

    async_add_entities(sensors)
    coordinator.register_sensors(sensors)


class HEMSConsigneSensor(SensorEntity):
    _attr_unit_of_measurement = "W"
    _attr_icon = "mdi:flash"
    _attr_should_poll = False

    def __init__(self, inverter):
        self.inverter = inverter
        self._attr_name = f"HEMS Consigne {inverter.name}"
        self._attr_unique_id = f"hems_consigne_{inverter.name}"

    @property
    def native_value(self):
        return round(self.inverter.consigne, 1)

    def update_from_engine(self):
        self.async_write_ha_state()
