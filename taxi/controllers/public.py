import logging

from aiohttp import web
from aiohttp.web import Request

from taxi.bl.utils import Coordinate
from taxi.bl.route import process_driver_route
from taxi.lib.exceptions import InvalidBodyError
from taxi.lib.metrics.metrics import coordinates_count
from taxi.lib.utils import (
    request_to_dict,
    validate_schema,
)

log = logging.getLogger(__name__)

BAD_REQUEST_CODE = web.HTTPBadRequest.status_code

HANDLE_DRIVER_DATA_REQUEST_SCHEMA = {
    'type': 'object',
    'properties': {
        'driver_id': {
            'type': 'integer',
        },
        'latitude': {
            'type': 'number',
        },
        'longitude': {
            'type': 'number',
        },
        'altitude': {
            'type': 'number',
        },
        'speed': {
            'type': 'number',
        },
    },
    'required': [
        'driver_id',
        'latitude',
        'longitude',
        'altitude',
        'speed',
    ],
}


async def handle_driver_data(request: Request):
    """
    ---
    description: Загрузка данных о мартшруте водителя.
    tags:
    - Driver data
    produces:
    - application/json
    parameters:
    - in: body
      name: driver data
      schema:
        type: object
        required:
        - driver_id
        - latitude
        - longitude
        - altitude
        - speed
        properties:
          driver_id:
            type: integer
            example: 1
          latitude:
            type: number
            example: 0.8
          longitude:
            type: number
            example: 0.9
          altitude:
            type: number
            example: 500
          speed:
            type: number
            example: 200
    responses:
        "200":
            description: Данные правильные и попали в обработку сохранились.
            schema:
                type: object
                properties:
                  success:
                    type: boolean
                    example: true

        "400":
            description: Ошибка при обработке данных, неверные данные.
            schema:
                type: object
                properties:
                  success:
                    type: boolean
                    example: false
    """

    try:
        data = await request_to_dict(request)
        await validate_schema(data, HANDLE_DRIVER_DATA_REQUEST_SCHEMA)
    except InvalidBodyError as e:
        log.info(f'Bad request to handle driver data. Error: {e.errors}')
        return web.json_response({'success': False}, status=BAD_REQUEST_CODE)

    coordinate = Coordinate(
        latitude=data['latitude'],
        longitude=data['longitude'],
        altitude=data['altitude'],
    )
    coordinates_count.inc()

    async with request.app['db'].acquire() as conn:
        await process_driver_route(
            conn=conn,
            driver_id=data['driver_id'],
            coordinate=coordinate,
            speed=data['speed'],
        )

    return web.json_response({'success': True})
