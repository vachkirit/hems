import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from . import DOMAIN


class HEMSOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        super().__init__()

        # ne PAS utiliser self.config_entry (réservé par HA)
        self._config_entry = config_entry

        # Base SAFE : options si présentes, sinon data
        self._inverters = list(
            config_entry.options.get(
                "inverters",
                config_entry.data.get("inverters", [])
            )
        )

    async def async_step_init(self, user_input=None):
        return await self.async_step_menu()

    # -------------------------------------------------
    # Menu principal
    # -------------------------------------------------
    async def async_step_menu(self, user_input=None):
        return self.async_show_menu(
            step_id="menu",
            menu_options={
                "add_inverter": "Ajouter un onduleur",
                "remove_inverter": "Supprimer un onduleur",
            },
        )

    # -------------------------------------------------
    # Ajouter un onduleur
    # -------------------------------------------------
    async def async_step_add_inverter(self, user_input=None):
        if user_input is not None:
            self._inverters.append(user_input)
            return await self.async_step_finish()

        schema = vol.Schema({
            vol.Required("name"): str,
            vol.Required("max_power"): int,
            vol.Optional("bidirectional_mode", default=False): bool,
            vol.Required("solar_sensor"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Required("soc_sensor"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Required("soc_min_sensor"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="number")
            ),
            vol.Required("soc_max_sensor"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="number")
            ),
        })

        return self.async_show_form(
            step_id="add_inverter",
            data_schema=schema,
        )

    # -------------------------------------------------
    # Supprimer un onduleur
    # -------------------------------------------------
    async def async_step_remove_inverter(self, user_input=None):
        if not self._inverters:
            return self.async_abort(reason="no_inverters")

        if user_input is not None:
            name = user_input["name"]
            self._inverters = [
                inv for inv in self._inverters
                if inv["name"] != name
            ]
            return await self.async_step_finish()

        schema = vol.Schema({
            vol.Required("name"): vol.In(
                [inv["name"] for inv in self._inverters]
            )
        })

        return self.async_show_form(
            step_id="remove_inverter",
            data_schema=schema,
        )


    # -------------------------------------------------
    # Finalisation
    # -------------------------------------------------
    async def async_step_finish(self, user_input=None):
        self.hass.config_entries.async_update_entry(
            self._config_entry,
            options={"inverters": self._inverters},
        )

        return self.async_abort(reason="configuration_updated - reboot HA")
