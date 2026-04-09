import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN, CONF_FUEL_TYPE, CONF_RADIUS, DEFAULT_RADIUS

FUEL_TYPES = [
    "ULP",
    "Diesel",
    "PULP",
    "LPG",
    "98RON",
]


class FuelWatchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=f"{user_input[CONF_FUEL_TYPE]} ({user_input[CONF_RADIUS]}km)",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_FUEL_TYPE): vol.In(FUEL_TYPES),
                vol.Required(CONF_RADIUS, default=DEFAULT_RADIUS): int,
            }),
        )
