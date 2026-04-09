from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_FUEL_TYPE
from .coordinator import FuelWatchCoordinator


SENSOR_TYPES = ["cheapest", "average", "most_expensive"]


async def async_setup_entry(hass, entry, async_add_entities):
    config = entry.data

    coordinator = FuelWatchCoordinator(
        hass,
        config[CONF_FUEL_TYPE],
        config["radius"]
    )

    await coordinator.async_config_entry_first_refresh()

    sensors = [
        FuelWatchSensor(coordinator, config, sensor_type)
        for sensor_type in SENSOR_TYPES
    ]

    async_add_entities(sensors)


class FuelWatchSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, config, sensor_type):
        super().__init__(coordinator)
        self._config = config
        self._type = sensor_type

    @property
    def name(self):
        return f"{self._type.replace('_', ' ').title()} Fuel"

    @property
    def state(self):
        data = self.coordinator.data
        if not data:
            return None

        if self._type == "average":
            return data["average"]

        return data[self._type]["price"]

    @property
    def unit_of_measurement(self):
        return "c/L"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if not data:
            return {}

        if self._type == "average":
            return {
                "stations_count": data["count"],
                "radius_km": self._config["radius"]
            }

        fuel = data[self._type]

        return {
            "station": fuel.get("trading_name"),
            "address": fuel.get("address"),
            "suburb": fuel.get("location"),
            "distance_km": fuel.get("distance"),
            "fuel_type": fuel.get("product"),
            "last_updated": fuel.get("date"),
        }

    @property
    def unique_id(self):
        return f"fuelwatch_{self._type}_{self._config['fuel_type']}_{self._config['radius']}"