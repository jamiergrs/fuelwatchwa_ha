import logging
import math
from datetime import timedelta
from typing import Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from fuelwatcher import FuelWatch

from .const import FUEL_TYPE_TO_PRODUCT, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(dlon / 2) ** 2
    )

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class FuelWatchCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, fuel_type, radius):
        super().__init__(
            hass,
            _LOGGER,
            name="FuelWatch Coordinator",
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

        self.client = FuelWatch()
        self.fuel_type = fuel_type
        self.radius = radius

    async def _async_update_data(self):
        try:
            product = FUEL_TYPE_TO_PRODUCT.get(self.fuel_type)
            if product is None:
                _LOGGER.error("Unsupported fuel type configured: %s", self.fuel_type)
                return None

            data = await self.hass.async_add_executor_job(
                self._fetch_stations,
                product,
            )

            if not data:
                _LOGGER.warning(
                    "FuelWatch returned no stations for fuel type %s", self.fuel_type
                )
                return None

            # Get Home Assistant location
            zone = self.hass.states.get("zone.home")
            if zone is None:
                _LOGGER.error("zone.home is missing; cannot calculate station distances")
                return None

            if "latitude" not in zone.attributes or "longitude" not in zone.attributes:
                _LOGGER.error(
                    "zone.home is missing latitude/longitude attributes: %s",
                    zone.attributes,
                )
                return None

            center_lat = zone.attributes["latitude"]
            center_lon = zone.attributes["longitude"]

            filtered = []

            for d in data:
                try:
                    lat = float(d["latitude"])
                    lon = float(d["longitude"])
                    price = float(d["price"])

                    distance = haversine(center_lat, center_lon, lat, lon)

                    if distance <= self.radius:
                        d["price"] = price
                        d["distance"] = round(distance, 2)
                        filtered.append(d)

                except Exception:
                    continue

            if not filtered:
                _LOGGER.info(
                    "No FuelWatch stations found within %skm of zone.home for %s "
                    "(fetched %s stations)",
                    self.radius,
                    self.fuel_type,
                    len(data),
                )
                return None

            cheapest = min(filtered, key=lambda x: x["price"])
            most_expensive = max(filtered, key=lambda x: x["price"])
            average = sum(d["price"] for d in filtered) / len(filtered)

            _LOGGER.debug(
                "FuelWatch matched %s of %s stations within %skm for %s",
                len(filtered),
                len(data),
                self.radius,
                self.fuel_type,
            )

            return {
                "cheapest": cheapest,
                "most_expensive": most_expensive,
                "average": round(average, 1),
                "count": len(filtered),
            }

        except Exception as e:
            _LOGGER.error("FuelWatch update failed: %s", e)
            return None

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
