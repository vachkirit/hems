from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN


async def async_setup_platform(
        hass: HomeAssistant,
        config,
        async_add_entities: AddEntitiesCallback,
        discovery_info=None,
):
    data = hass.data.get(DOMAIN)
    if not data:
        return

    engine = data.get("engine")
    coordinator = data.get("coordinator")

    # Défensif : on ne suppose rien
    if not engine or not coordinator:
        return

    sensors = [
        HEMSConsigneSensor(inv)
        for inv in engine.context.inverters
    ]

    if not sensors:
        return

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
