from typing import Dict, Any, Tuple
import asyncio
import random
import requests

from taxi.bl.constants import CITIES_COORDINATES_MAP
from taxi.config import get_config


def get_request_data(driver_id: int, city: str) -> Dict[str, Any]:

    def _generate_coordinates(
        city_coordinates: Dict[str, Any],
    ) -> Tuple[float, float, float]:
        x = random.uniform(
            city_coordinates['latitude_min'],
            city_coordinates['latitude_max']
        )
        y = random.uniform(
            city_coordinates['longitude_min'],
            city_coordinates['longitude_max']
        )
        z = random.uniform(
            city_coordinates['altitude_min'] - 100,
            city_coordinates['altitude_max'] + 100
        )
        return x, y, z

    coordinates = CITIES_COORDINATES_MAP.get(city)
    latitude, longitude, altitude = _generate_coordinates(coordinates)

    return {
        'driver_id': driver_id,
        'latitude': latitude,
        'longitude': longitude,
        'altitude': altitude,
        'speed': random.randint(10000, 20000)
    }


async def request_http(
    loop: asyncio.AbstractEventLoop,
    url: str,
    driver_id: int,
    city: str,
) -> None:
    data = get_request_data(driver_id, city)

    response = await loop.run_in_executor(None, requests.post, url, None, data)

    if response.ok:
        print(f'Success send data about driver #{driver_id}')
    else:
        print(f'Cannot send request to {url}: {response.status_code} code')
        exit()


async def simulate(
    loop: asyncio.AbstractEventLoop,
    url: str,
    drivers_count: int,
    delay: float,
    city: str,
) -> None:
    coordinates = CITIES_COORDINATES_MAP.get(city)
    if not coordinates:
        return None

    while True:
        await request_http(
            loop=loop,
            url=url,
            driver_id=random.randint(1, drivers_count),
            city=city,
        )
        await asyncio.sleep(delay)


def get_url(config: Dict[str, Any]) -> str:
    host = config['host']
    port = config['port']
    endpoint = 'handle_driver_data'
    return f'http://{host}:{port}/{endpoint}'


async def main():
    loop = asyncio.get_event_loop()
    app_config = get_config()
    url = get_url(app_config)

    drivers_count = input('Drivers count: ')
    delay = input('Delay: ')
    city = 'lviv'

    try:
        drivers_count = int(drivers_count)
        delay = float(delay)
    except ValueError:
        print('Invalid data')
        exit()

    await simulate(
        loop=loop,
        url=url,
        drivers_count=drivers_count,
        delay=delay,
        city=city,
    )

general_loop = asyncio.get_event_loop()
general_loop.run_until_complete(main())
