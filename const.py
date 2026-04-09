DOMAIN = "fuelwatch_ha"

CONF_FUEL_TYPE = "fuel_type"
CONF_RADIUS = "radius"

DEFAULT_NAME = "Fuel Prices"
DEFAULT_RADIUS = 10  # km

SCAN_INTERVAL = 3600  # 1hr

FUEL_TYPE_TO_PRODUCT = {
    "ULP": 1,
    "PULP": 2,
    "Diesel": 4,
    "LPG": 5,
    "98RON": 6,
}
