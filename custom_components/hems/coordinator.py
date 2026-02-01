import logging

from homeassistant.core import Event, callback
from homeassistant.const import EVENT_STATE_CHANGED

_LOGGER = logging.getLogger(__name__)

class HEMSCoordinator:
    """
    Adaptateur Home Assistant → moteur HEMS
    Écoute tous les changements d’état via le bus HA.
    """

    def __init__(self, hass, engine, entity_mapping):
        self.hass = hass
        self.engine = engine
        self.entity_mapping = entity_mapping
        self.sensors = []
        self._unsub = None

    # -----------------------------------------------------
    # Lifecycle
    # -----------------------------------------------------
    async def async_start(self):
        _LOGGER.info("HEMSCoordinator | start (EVENT_STATE_CHANGED)")

        # Écoute globale CORRECTE
        self._unsub = self.hass.bus.async_listen(
            EVENT_STATE_CHANGED,
            self._handle_event,
        )

        # Initialisation immédiate
        for entity_id in self.entity_mapping:
            state = self.hass.states.get(entity_id)
            _LOGGER.info(
                "HEMS | INIT | %s -> %r",
                entity_id,
                state.state if state else None,
            )
            if state:
                self._apply_state(entity_id, state.state)

        # Calcul initial
        self.engine.update()
        self._notify_sensors()

    async def async_stop(self):
        if self._unsub:
            self._unsub()
            self._unsub = None

    # -----------------------------------------------------
    # Event handling
    # -----------------------------------------------------
    @callback
    def _handle_event(self, event: Event):
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")

        if entity_id not in self.entity_mapping:
            return

        if not new_state:
            return

        _LOGGER.info(
            "HEMS | EVENT | %s -> %r",
            entity_id,
            new_state.state,
        )

        self._apply_state(entity_id, new_state.state)
        self.engine.update()
        self._notify_sensors()

    # -----------------------------------------------------
    # Mapping HA → moteur
    # -----------------------------------------------------
    def _apply_state(self, entity_id: str, state):
        if state in ("unknown", "unavailable", None):
            return

        if entity_id.startswith("input_select"):
            value = str(state).strip()
        else:
            try:
                value = float(state)
            except (ValueError, TypeError):
                return

        _LOGGER.info(
            "HEMS | APPLY | %s = %r",
            entity_id,
            value,
        )

        self.entity_mapping[entity_id](value)

    # -----------------------------------------------------
    # Sensors notification
    # -----------------------------------------------------
    def register_sensors(self, sensors):
        self.sensors = sensors

    def _notify_sensors(self):
        for sensor in self.sensors:
            sensor.update_from_engine()
