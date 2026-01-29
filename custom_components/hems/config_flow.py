import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

DOMAIN = "hems"


class HEMSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._data = {}

    # -------------------------------------------------
    # Étape 1 : configuration globale
    # -------------------------------------------------
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self._data = dict(user_input)
            self._data["inverters"] = []
            return await self.async_step_add_inverter()

        schema = vol.Schema({
            vol.Required("house_power_sensor"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Required("car_power_sensor"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )

    # -------------------------------------------------
    # Étape 2 : ajout d’un onduleur
    # -------------------------------------------------
    async def async_step_add_inverter(self, user_input=None):
        if user_input is not None:
            self._data["inverters"].append(user_input)
            return await self.async_step_menu()

        schema = vol.Schema({
            vol.Required("name"): str,
            vol.Required("max_power"): int,
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
    # Étape 3 : menu (ajouter / terminer)
    # -------------------------------------------------
    async def async_step_menu(self, user_input=None):
        return self.async_show_menu(
            step_id="menu",
            menu_options={
                "add_inverter": "Ajouter un autre onduleur",
                "finish": "Terminer la configuration",
            },
        )

    async def async_step_finish(self, user_input=None):
        return self.async_create_entry(
            title="HEMS",
            data=self._data,
        )
