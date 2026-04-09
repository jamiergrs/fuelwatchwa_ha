import voluptuous as vol

from homeassistant import config_entries

from .const import (
    CONF_FUEL_TYPE,
    CONF_LATITUDE,
    CONF_LOCATION_MODE,
    CONF_LONGITUDE,
    CONF_NAME,
    CONF_RADIUS,
    CONF_ZONE_NAME,
    DEFAULT_NAME,
    DEFAULT_RADIUS,
    DEFAULT_ZONE_NAME,
    DOMAIN,
    LOCATION_MODE_COORDINATES,
    LOCATION_MODE_HOME,
    LOCATION_MODE_OPTIONS,
    LOCATION_MODE_ZONE,
)

FUEL_TYPES = [
    "ULP",
    "Diesel",
    "PULP",
    "LPG",
    "98RON",
]


class FuelWatchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            data, errors = self._validate_user_input(user_input)
            if not errors:
                return self.async_create_entry(
                    title=data[CONF_NAME],
                    data=data,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                    vol.Required(CONF_FUEL_TYPE): vol.In(FUEL_TYPES),
                    vol.Required(CONF_RADIUS, default=DEFAULT_RADIUS): int,
                    vol.Required(
                        CONF_LOCATION_MODE, default=LOCATION_MODE_HOME
                    ): vol.In(LOCATION_MODE_OPTIONS),
                    vol.Optional(CONF_ZONE_NAME, default=DEFAULT_ZONE_NAME): str,
                    vol.Optional(CONF_LATITUDE, default=""): str,
                    vol.Optional(CONF_LONGITUDE, default=""): str,
                }
            ),
            errors=errors,
        )

    def _validate_user_input(self, user_input):
        data = dict(user_input)
        errors = {}

        name = data.get(CONF_NAME, "").strip()
        if not name:
            errors[CONF_NAME] = "name_required"
        else:
            data[CONF_NAME] = name

        location_mode = data.get(CONF_LOCATION_MODE, LOCATION_MODE_HOME)
        zone_name = data.get(CONF_ZONE_NAME, "").strip()
        data[CONF_ZONE_NAME] = zone_name

        if location_mode == LOCATION_MODE_ZONE and not zone_name:
            errors[CONF_ZONE_NAME] = "zone_required"

        if location_mode == LOCATION_MODE_COORDINATES:
            latitude = self._parse_coordinate(
                data.get(CONF_LATITUDE, ""), CONF_LATITUDE, -90, 90, errors
            )
            longitude = self._parse_coordinate(
                data.get(CONF_LONGITUDE, ""), CONF_LONGITUDE, -180, 180, errors
            )
            data[CONF_LATITUDE] = latitude
            data[CONF_LONGITUDE] = longitude
        else:
            data[CONF_LATITUDE] = None
            data[CONF_LONGITUDE] = None

        if location_mode == LOCATION_MODE_HOME:
            data[CONF_ZONE_NAME] = DEFAULT_ZONE_NAME

        return data, errors

    def _parse_coordinate(self, raw_value, field, min_value, max_value, errors):
        value = str(raw_value).strip()
        if not value:
            errors[field] = f"{field}_required"
            return None

        try:
            coordinate = float(value)
        except ValueError:
            errors[field] = f"{field}_invalid"
            return None

        if coordinate < min_value or coordinate > max_value:
            errors[field] = f"{field}_invalid"
            return None

        return coordinate
