from datetime import datetime, timezone, timedelta

import pytest

from taxi.bl.route import (
    ProcessDescription,
    process_driver_speed,
    process_driver_altitude,
)
from taxi.bl.utils import (
    Coordinate,
    calculate_distance_between_coordinates,
    calculate_distance_by_speed,
)


class TestDriverRoute:
    driver_id = 1
    latitude = 0.7
    longitude = 0.7
    altitude = 500
    speed = 60


@pytest.mark.asyncio
async def test_process_driver_altitude():
    # test invalid city
    coordinate = Coordinate(
        latitude=100,
        longitude=100,
        altitude=100
    )
    driver_incorrect_altitude = process_driver_altitude(coordinate)
    assert driver_incorrect_altitude == ProcessDescription(
        detect=False, description='Invalid city coordinates.'
    )

    # test valid altitude
    coordinate = Coordinate(
        latitude=TestDriverRoute.latitude,
        longitude=TestDriverRoute.longitude,
        altitude=TestDriverRoute.altitude
    )
    driver_incorrect_altitude = process_driver_altitude(coordinate)
    assert driver_incorrect_altitude == ProcessDescription(
        detect=False, description=(
            f'Driver altitude {coordinate.altitude} '
            f'is normal for city Lviv.'
        )
    )

    # test invalid altitude
    coordinate = Coordinate(
        latitude=TestDriverRoute.latitude,
        longitude=TestDriverRoute.longitude,
        altitude=TestDriverRoute.altitude + 300,
    )
    driver_incorrect_altitude = process_driver_altitude(coordinate)
    assert driver_incorrect_altitude == ProcessDescription(
        detect=True, description=(
            f'Driver has incorrect altitude {coordinate.altitude} '
            f'for city Lviv.'
        )
    )


@pytest.mark.asyncio
async def test_process_driver_speed():
    coordinate = Coordinate(
        latitude=TestDriverRoute.latitude,
        longitude=TestDriverRoute.longitude,
        altitude=TestDriverRoute.altitude
    )

    # driver without previous route
    driver_over_speed = process_driver_speed(
        None, TestDriverRoute.speed, coordinate
    )
    assert driver_over_speed == ProcessDescription(
        detect=False, description='New driver route.'
    )

    # test driver over speed
    driver_route = {
        'driver_id': TestDriverRoute.driver_id,
        'latitude': TestDriverRoute.latitude + 1,
        'longitude': TestDriverRoute.longitude + 1,
        'altitude': TestDriverRoute.altitude,
        'speed': TestDriverRoute.speed,
        'date_created': datetime.now(timezone.utc) - timedelta(seconds=10),
    }
    driver_over_speed = process_driver_speed(
        driver_route, TestDriverRoute.speed, coordinate
    )
    coordinates_distance = calculate_distance_between_coordinates(
        driver_route=driver_route,
        coordinate=coordinate,
    )
    speed_distance = calculate_distance_by_speed(
        driver_route=driver_route,
        speed=TestDriverRoute.speed,
    )
    assert driver_over_speed == ProcessDescription(
        detect=True, description=(
            f'Distance by speed is {speed_distance} but '
            f'the distance between the points is {coordinates_distance}.'
        )
    )

    # test driver not over speed
    driver_route = {
        'driver_id': TestDriverRoute.driver_id,
        'latitude': TestDriverRoute.latitude,
        'longitude': TestDriverRoute.longitude + 0.00001,
        'altitude': TestDriverRoute.altitude,
        'speed': TestDriverRoute.speed,
        'date_created': datetime.now(timezone.utc) - timedelta(seconds=10),
    }
    driver_over_speed = process_driver_speed(
        driver_route, TestDriverRoute.speed, coordinate
    )
    coordinates_distance = calculate_distance_between_coordinates(
        driver_route=driver_route,
        coordinate=coordinate,
    )
    speed_distance = calculate_distance_by_speed(
        driver_route=driver_route,
        speed=TestDriverRoute.speed,
    )

    assert driver_over_speed == ProcessDescription(
        detect=False, description=(
            f'Distance by speed is {speed_distance} but '
            f'the distance between the points is {coordinates_distance}.'
        )
    )
