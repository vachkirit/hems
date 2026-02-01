from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfPower

from . import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    engine = data["engine"]
    coordinator = data["coordinator"]

    sensors = []

    for inv in engine.context.inverters:
        sensors.append(HEMSConsigneSensor(inv))
        sensors.append(HEMSConsigneACSensor(inv))

    async_add_entities(sensors)
    coordinator.register_sensors(sensors)


# -------------------------------------------------
# Capteur CONSIGNE
# -------------------------------------------------
class HEMSConsigneSensor(SensorEntity):
    _attr_unit_of_measurement = UnitOfPower.WATT
    _attr_icon = "mdi:flash"
    _attr_should_poll = False

    def __init__(self, inverter):
        self.inverter = inverter
        self._attr_name = f"HEMS Consigne {inverter.name}"
        self._attr_unique_id = f"hems_consigne_{inverter.name}"

    @property
    def native_value(self):
        # ARRONDI A LA DIZAINE DE WATTS INFERIEUR
        return int(self.inverter.consigne // 10 * 10)

    @property
    def device_info(self):
        return {
            "identifiers": {("hems", self.inverter.name)},
            "name": self.inverter.name,
            "manufacturer": "HEMS",
            "model": "Inverter",
        }

    def update_from_engine(self):
        self.async_write_ha_state()


# -------------------------------------------------
# Capteur CONSIGNE AC
# -------------------------------------------------
class HEMSConsigneACSensor(SensorEntity):
    _attr_unit_of_measurement = UnitOfPower.WATT
    _attr_icon = "mdi:flash"
    _attr_should_poll = False

    def __init__(self, inverter):
        self.inverter = inverter
        self._attr_name = f"HEMS Consigne AC {inverter.name}"
        self._attr_unique_id = f"hems_consigne_ac_{inverter.name}"

    @property
    def native_value(self):
        return self.inverter.consigne_ac

    @property
    def device_info(self):
        return {
            "identifiers": {("hems", self.inverter.name)},
            "name": self.inverter.name,
            "manufacturer": "HEMS",
            "model": "Inverter",
        }

    def update_from_engine(self):
        self.async_write_ha_state()
