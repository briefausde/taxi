import logging
from typing import NamedTuple, Optional

from aiopg.sa import SAConnection
from aiopg.sa.result import RowProxy

from taxi.bl.constants import CITIES_COORDINATES_MAP
from taxi.bl.utils import (
    Coordinate,
    calculate_distance_between_coordinates,
    calculate_distance_by_speed,
    get_city_by_coordinates,
)
from taxi.lib.db.queries import (
    select_last_driver_route,
    insert_driver_route,
    insert_route_description,
)
from taxi.lib.metrics.metrics import (
    invalid_altitude_count,
    unique_drivers_count,
    over_speed_drivers_count,
)

log = logging.getLogger(__name__)


class ProcessDescription(NamedTuple):
    detect: bool
    description: str


def process_driver_altitude(coordinate: Coordinate) -> ProcessDescription:
    """Check is altitude are in the city coordinate range"""
    city = get_city_by_coordinates(
        latitude=coordinate.latitude,
        longitude=coordinate.longitude,
    )
    city_coordinates = CITIES_COORDINATES_MAP.get(city)
    if not city_coordinates:
        return ProcessDescription(
            detect=False,
            description='Invalid city coordinates.'
        )

    altitude_min = city_coordinates['altitude_min']
    altitude_max = city_coordinates['altitude_max']

    if altitude_min <= coordinate.altitude <= altitude_max:
        return ProcessDescription(
            detect=False,
            description=(
                f'Driver altitude {coordinate.altitude} '
                f'is normal for city {city.capitalize()}.'
            )
        )

    return ProcessDescription(
        detect=True,
        description=(
            f'Driver has incorrect altitude {coordinate.altitude} '
            f'for city {city.capitalize()}.'
        )
    )


def process_driver_speed(
    driver_route: Optional[RowProxy],
    speed: float,
    coordinate: Coordinate,
) -> ProcessDescription:
    """
    Check if driver over speed in distance.

    Calculated as the average speed at the previous distance plus the speed at
    the current distance divided by the time difference between the present
    and the past. And if the length between the points is greater than
    the calculated length, then the driver has over speed.
    """

    def _get_description(distance_1: float, distance_2: float) -> str:
        return (
            f'Distance by speed is {distance_1} but '
            f'the distance between the points is {distance_2}.'
        )

    if not driver_route:
        return ProcessDescription(
            detect=False,
            description='New driver route.'
        )

    coordinates_distance = calculate_distance_between_coordinates(
        driver_route=driver_route,
        coordinate=coordinate,
    )
    speed_distance = calculate_distance_by_speed(
        driver_route=driver_route,
        speed=speed,
    )

    if coordinates_distance >= speed_distance:
        return ProcessDescription(
            detect=True,
            description=_get_description(speed_distance, coordinates_distance)
        )

    return ProcessDescription(
        detect=False,
        description=_get_description(speed_distance, coordinates_distance)
    )


async def process_driver_route(
    conn: SAConnection,
    driver_id: int,
    coordinate: Coordinate,
    speed: float,
) -> None:
    driver_route = await select_last_driver_route(conn, driver_id=driver_id)

    if not driver_route:
        log.info(f'Registered new #{driver_id} driver route')
        unique_drivers_count.inc()

    driver_incorrect_altitude = process_driver_altitude(coordinate=coordinate)
    if driver_incorrect_altitude.detect:
        log.info(f'Driver has incorrect altitude', {
            'driver_id': driver_id,
            'description': driver_incorrect_altitude.description,
        })
        invalid_altitude_count.inc()

    driver_over_speed = process_driver_speed(
        driver_route=driver_route,
        speed=speed,
        coordinate=coordinate,
    )
    if driver_over_speed.detect:
        log.info(f'Driver over speed', {
            'driver_id': driver_id,
            'description': driver_over_speed.detect,
        })
        over_speed_drivers_count.inc()

    driver_route_id = await insert_driver_route(
        conn,
        driver_id=driver_id,
        coordinate=coordinate,
        speed=speed,
    )

    await insert_route_description(
        conn=conn,
        driver_route_id=driver_route_id,
        description=(
            f'{driver_incorrect_altitude.description} '
            f'{driver_over_speed.description}'
        ),
        is_correct_driver_altitude=driver_incorrect_altitude.detect,
        is_driver_over_speed=driver_over_speed.detect,
    )
