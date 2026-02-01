import logging
from homeassistant.core import HomeAssistant

from .engine.core import Engine
from .engine.inverter import Inverter
from .coordinator import HEMSCoordinator

_LOGGER = logging.getLogger(__name__)
DOMAIN = "hems"

async def async_setup_entry(hass, entry):
    _LOGGER.info("HEMS | setup entry %s", entry.entry_id)

    engine = Engine(
        mode=None,
        power_consumption_total=0,
        power_consumption_car=0,
        inverters=[],
    )

    entity_mapping = {}

    # -----------------------------
    # Capteurs globaux
    # -----------------------------
    house_power_sensor = entry.data["house_power_sensor"]
    car_power_sensor = entry.data["car_power_sensor"]

    entity_mapping[house_power_sensor] = lambda v: setattr(
        engine.context, "power_consumption_total", v
    )
    entity_mapping[car_power_sensor] = lambda v: setattr(
        engine.context, "power_consumption_car", v
    )

    # -----------------------------
    # Onduleurs dynamiques
    # -----------------------------
    engine.context.inverters.clear()
    inverters_cfg = entry.options.get("inverters",entry.data.get("inverters", [])
                                      )
    for inv_cfg in inverters_cfg:
        inverter = Inverter(
            name=inv_cfg["name"],
            max_power=inv_cfg["max_power"],
            bidirectional_mode=inv_cfg.get("bidirectional_mode", False),
        )

        engine.context.inverters.append(inverter)

        # important : capturer inverter avec valeur par défaut
        entity_mapping[inv_cfg["solar_sensor"]] = \
            (lambda i: lambda v: setattr(i, "solar", v))(inverter)

        entity_mapping[inv_cfg["soc_sensor"]] = \
            (lambda i: lambda v: setattr(i, "soc", v))(inverter)

        entity_mapping[inv_cfg["soc_min_sensor"]] = \
            (lambda i: lambda v: setattr(i, "soc_min", v))(inverter)

        entity_mapping[inv_cfg["soc_max_sensor"]] = \
            (lambda i: lambda v: setattr(i, "soc_max", v))(inverter)

    # -----------------------------
    # Coordinator
    # -----------------------------
    coordinator = HEMSCoordinator(hass, engine, entity_mapping)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "engine": engine,
        "coordinator": coordinator,
    }

    await coordinator.async_start()
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "select"])


    return True

async def async_unload_entry(hass, entry):
    data = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)

    if not data:
        return True

    coordinator = data.get("coordinator")

    if coordinator:
        await coordinator.async_stop()

    # Décharger les plateformes (sensor, select, etc.)
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, ["sensor", "select"]
    )

    return unload_ok
