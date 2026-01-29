import logging
from homeassistant.core import HomeAssistant

from .engine.core import Engine
from .engine.inverter import Inverter
from .coordinator import HEMSCoordinator

_LOGGER = logging.getLogger(__name__)
DOMAIN = "hems"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    _LOGGER.info("HEMS | setup")

    engine = Engine(
        mode="Normal",
        power_consumption_total=0,
        power_consumption_car=0,
        inverters=[],
    )

    hyper = Inverter("hyper_2000", max_power=1200)
    engine.context.inverters.append(hyper)

    entity_mapping = {
        # Mode
        "input_select.hems_mode": lambda v: setattr(
            engine.context, "mode", v.strip()
        ),

        # Consommations
        "sensor.hems_maison_consommation": lambda v: setattr(
            engine.context, "power_consumption_total", v
        ),
        "input_number.hems_voiture_consommation": lambda v: setattr(
            engine.context, "power_consumption_car", v
        ),

        # Onduleur Hyper
        "sensor.solaire_hyper2000_puissance_instantannee": lambda v: setattr(
            hyper, "solar", v
        ),
        "sensor.hyper_2000_electric_level": lambda v: setattr(
            hyper, "soc", v
        ),
        "number.hyper_2000_min_soc": lambda v: setattr(
            hyper, "soc_min", v
        ),
        "number.hyper_2000_soc_set": lambda v: setattr(
            hyper, "soc_max", v
        ),
    }


    coordinator = HEMSCoordinator(hass, engine, entity_mapping)

    # IMPORTANT : stocker AVANT async_start
    hass.data[DOMAIN] = {
        "engine": engine,
        "coordinator": coordinator,
        "inverters": {"hyper_2000": hyper},
    }

    await coordinator.async_start()

    return True

