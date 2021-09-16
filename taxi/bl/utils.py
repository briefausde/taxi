from typing import NamedTuple, Optional
from datetime import datetime, timezone

from aiopg.sa.result import RowProxy
from geopy.distance import geodesic

from taxi.bl.constants import CITIES_COORDINATES_MAP


class Coordinate(NamedTuple):
    latitude: float
    longitude: float
    altitude: float


def get_city_by_coordinates(latitude: float, longitude: float) -> Optional[str]:
    """If the coordinates are in the zone of a city, return this city name"""
    for city, coordinates in CITIES_COORDINATES_MAP.items():
        latitude_min = coordinates['latitude_min']
        latitude_max = coordinates['latitude_max']
        longitude_min = coordinates['longitude_min']
        longitude_max = coordinates['longitude_max']

        if (
            latitude_min <= latitude <= latitude_max and
            longitude_min <= longitude <= longitude_max
        ):
            return city

    return None


def get_distance_between_coordinates_in_km(
    previous: Coordinate,
    current: Coordinate,
) -> float:
    return geodesic(
        (previous.latitude, previous.longitude),
        (current.latitude, current.longitude)
    ).kilometers


def calculate_distance_between_coordinates(
    driver_route: RowProxy,
    coordinate: Coordinate,
) -> float:
    previous_coordinate = Coordinate(
        latitude=driver_route['latitude'],
        longitude=driver_route['longitude'],
        altitude=driver_route['altitude'],
    )
    return get_distance_between_coordinates_in_km(
        previous=previous_coordinate,
        current=coordinate,
    )


def calculate_distance_by_speed(
    driver_route: RowProxy,
    speed: float,
) -> float:
    previous_speed = driver_route['speed']
    previous_datetime = driver_route['date_created']

    route_time = datetime.now(timezone.utc) - previous_datetime

    return ((previous_speed + speed) / 2) * (route_time.seconds / 3600)
