import logging
from datetime import datetime, timezone

from aiopg.sa import SAConnection
from aiopg.sa.result import RowProxy

from taxi.bl.coordinates import (
    Coordinate,
    is_correct_altitude,
    get_distance_between_coordinates_in_km,
)
from taxi.lib.db.queries import (
    select_driver_route,
    insert_driver_route,
    insert_route_description,
)
from taxi.lib.metrics.metrics import (
    invalid_altitude_count,
    unique_drivers_count,
    over_speed_drivers_count,
)

log = logging.getLogger(__name__)


def is_distance_over_speed(
    driver_route: RowProxy,
    speed: float,
    coordinate: Coordinate,
) -> bool:
    """
    Check if driver over speed in distance.

    Calculated as the average speed at the previous distance plus the speed at
    the current distance divided by the time difference between the present
    and the past. And if the calculated length is greater than the length
    between the points, then the driver has over speed.
    """

    previous_speed = driver_route['speed']
    previous_datetime = driver_route['date_created']
    previous_coordinate = Coordinate(
        latitude=driver_route['latitude'],
        longitude=driver_route['longitude'],
        altitude=driver_route['altitude'],
    )

    distance = get_distance_between_coordinates_in_km(
        previous=previous_coordinate,
        current=coordinate,
    )

    route_time = datetime.now(timezone.utc) - previous_datetime

    distance_based_on_speed = (
        ((previous_speed + speed) / 2) * (route_time.seconds / 3600)
    )

    if distance_based_on_speed >= distance:
        return True

    return False


async def process_driver_route(
    conn: SAConnection,
    driver_id: int,
    coordinate: Coordinate,
    speed: float,
) -> None:
    driver_route = await select_driver_route(conn, driver_id=driver_id)

    await insert_driver_route(
        conn,
        driver_id=driver_id,
        coordinate=coordinate,
        speed=speed,
    )

    is_correct_driver_altitude = True
    if not is_correct_altitude(coordinate=coordinate):
        is_correct_driver_altitude = False
        log.info(f'Driver #{driver_id} has incorrect altitude')
        invalid_altitude_count.inc()

    if not driver_route:
        log.info(f'Registered new #{driver_id} driver')
        unique_drivers_count.inc()
        return None

    is_driver_over_speed = False
    if is_distance_over_speed(
        driver_route=driver_route,
        speed=speed,
        coordinate=coordinate,
    ):
        is_driver_over_speed = True
        log.info(f'Driver #{driver_id} has over speed')
        over_speed_drivers_count.inc()

    await insert_route_description(
        conn=conn,
        driver_route_id=driver_route['id'],
        is_driver_over_speed=is_driver_over_speed,
        is_correct_driver_altitude=is_correct_driver_altitude,
    )
