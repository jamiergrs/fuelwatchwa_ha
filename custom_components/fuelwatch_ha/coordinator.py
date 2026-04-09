import logging
import math
from datetime import timedelta
from typing import Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import slugify

from fuelwatcher import FuelWatch

from .const import (
    CONF_FUEL_TYPE,
    CONF_LATITUDE,
    CONF_LOCATION_MODE,
    CONF_LONGITUDE,
    CONF_NAME,
    CONF_RADIUS,
    CONF_ZONE_NAME,
    DEFAULT_ZONE_NAME,
    FUEL_TYPE_TO_PRODUCT,
    LOCATION_MODE_COORDINATES,
    LOCATION_MODE_HOME,
    LOCATION_MODE_ZONE,
    SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


def haversine(lat1, lon1, lat2, lon2):
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class FuelWatchCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, config, entry_title):
        super().__init__(
            hass,
            _LOGGER,
            name="FuelWatch Coordinator",
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

        self.client = FuelWatch()
        self.name = config.get(CONF_NAME) or entry_title
        self.fuel_type = config[CONF_FUEL_TYPE]
        self.radius = config[CONF_RADIUS]
        self.location_mode = config.get(CONF_LOCATION_MODE, LOCATION_MODE_HOME)
        self.zone_name = config.get(CONF_ZONE_NAME, DEFAULT_ZONE_NAME)
        self.latitude = config.get(CONF_LATITUDE)
        self.longitude = config.get(CONF_LONGITUDE)

    async def _async_update_data(self):
        try:
            product = FUEL_TYPE_TO_PRODUCT.get(self.fuel_type)
            if product is None:
                _LOGGER.error("Unsupported fuel type configured: %s", self.fuel_type)
                return None

            center_lat, center_lon, location_label = self._resolve_center_point()

            data = await self.hass.async_add_executor_job(
                self._fetch_stations,
                product,
            )

            if not data:
                _LOGGER.warning(
                    "FuelWatch returned no stations for fuel type %s", self.fuel_type
                )
                return None

            filtered = []

            for station in data:
                try:
                    lat = float(station["latitude"])
                    lon = float(station["longitude"])
                    price = float(station["price"])

                    distance = haversine(center_lat, center_lon, lat, lon)

                    if distance <= self.radius:
                        station["price"] = price
                        station["distance"] = round(distance, 2)
                        filtered.append(station)
                except Exception:
                    _LOGGER.debug("Skipping invalid station payload: %s", station)
                    continue

            if not filtered:
                _LOGGER.info(
                    "No FuelWatch stations found within %skm of %s for %s "
                    "(fetched %s stations)",
                    self.radius,
                    location_label,
                    self.fuel_type,
                    len(data),
                )
                return None

            cheapest = min(filtered, key=lambda item: item["price"])
            most_expensive = max(filtered, key=lambda item: item["price"])
            average = sum(item["price"] for item in filtered) / len(filtered)

            _LOGGER.debug(
                "FuelWatch matched %s of %s stations within %skm for %s using %s",
                len(filtered),
                len(data),
                self.radius,
                self.fuel_type,
                location_label,
            )

            return {
                "cheapest": cheapest,
                "most_expensive": most_expensive,
                "average": round(average, 1),
                "count": len(filtered),
                "location_label": location_label,
                "location_mode": self.location_mode,
            }
        except Exception as err:
            _LOGGER.error("FuelWatch update failed: %s", err)
            return None

    def _resolve_center_point(self):
        if self.location_mode == LOCATION_MODE_COORDINATES:
            if self.latitude is None or self.longitude is None:
                raise ValueError("Latitude/longitude must be configured for coordinates")

            return float(self.latitude), float(self.longitude), self.name

        zone_ref = self.zone_name or DEFAULT_ZONE_NAME
        if self.location_mode == LOCATION_MODE_HOME:
            zone_ref = DEFAULT_ZONE_NAME

        entity_id = zone_ref if "." in zone_ref else f"zone.{slugify(zone_ref)}"
        zone = self.hass.states.get(entity_id)
        if zone is None:
            raise ValueError(f"Configured zone not found: {entity_id}")

        if "latitude" not in zone.attributes or "longitude" not in zone.attributes:
            raise ValueError(
                f"Configured zone missing latitude/longitude attributes: {entity_id}"
            )

        location_label = zone.name or entity_id
        return zone.attributes["latitude"], zone.attributes["longitude"], location_label

    def _fetch_stations(self, product: int) -> list[dict[str, Any]]:
        """Query FuelWatch and normalize the returned station objects."""
        self.client.query(product=product)

        if hasattr(self.client, "stations"):
            return self._normalize_station_objects(self.client.stations)

        xml_stations = getattr(self.client, "xml", None)
        if xml_stations is None:
            xml_stations = getattr(self.client, "get_xml", None)

        if xml_stations is None:
            raise AttributeError(
                "FuelWatch client does not expose either 'stations' or 'xml/get_xml'"
            )

        return self._normalize_station_dicts(xml_stations)

    def _normalize_station_objects(self, stations: list[Any]) -> list[dict[str, Any]]:
        """Normalize newer fuelwatcher dataclass-style results."""
        normalized = []
        for station in stations:
            normalized.append(
                {
                    "price": station.price,
                    "latitude": station.latitude,
                    "longitude": station.longitude,
                    "trading_name": station.trading_name,
                    "address": station.address,
                    "location": station.location,
                    "product": self.fuel_type,
                    "date": station.date,
                }
            )

        return normalized

    def _normalize_station_dicts(
        self,
        stations: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Normalize older fuelwatcher dict-style results."""
        normalized = []
        for station in stations:
            price = station.get("price")
            latitude = station.get("latitude")
            longitude = station.get("longitude")
            trading_name = station.get("trading_name") or station.get("trading-name")

            if price is None or latitude is None or longitude is None:
                _LOGGER.debug("Skipping incomplete FuelWatch station payload: %s", station)
                continue

            normalized.append(
                {
                    "price": price,
                    "latitude": latitude,
                    "longitude": longitude,
                    "trading_name": trading_name,
                    "address": station.get("address"),
                    "location": station.get("location"),
                    "product": self.fuel_type,
                    "date": station.get("date"),
                }
            )

        return normalized
