from typing import NamedTuple, Optional

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


def is_correct_altitude(coordinate: Coordinate) -> bool:
    """Check is altitude are in the city coordinate range"""
    city = get_city_by_coordinates(
        latitude=coordinate.latitude,
        longitude=coordinate.longitude,
    )
    city_coordinates = CITIES_COORDINATES_MAP.get(city)
    if not city_coordinates:
        return False

    altitude_min = city_coordinates['altitude_min']
    altitude_max = city_coordinates['altitude_max']

    if altitude_min <= coordinate.altitude <= altitude_max:
        return True

    return False


def get_distance_between_coordinates_in_km(
    previous: Coordinate,
    current: Coordinate,
) -> float:
    return geodesic(
        (previous.latitude, previous.longitude),
        (current.latitude, current.longitude)
    ).kilometers
