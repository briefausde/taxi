import logging

from aiohttp import web

log = logging.getLogger(__name__)


async def healthcheck(request: web.Request) -> web.Response:
    """
    ---
    description: Информация про состояние сервиса.
    tags:
    - Health check
    produces:
    - application/json
    responses:
        "200":
            description: С базой все впорядке.
            schema:
                type: object
                properties:
                  success:
                    type: boolean
                    example: true

        "500":
            description: Проблемы с базой.
            schema:
                type: object
                properties:
                  success:
                    type: boolean
                    example: false
    """

    try:
        async with request.app['db'].acquire() as conn:
            await conn.execute('SELECT version();')
    except Exception as error:
        db_name = request.app['config']['db']['database']
        log.error(f'Database {db_name} is unavailable', extra={
            'error': error,
        })
        return web.json_response({'status': 'bad'}, status=500)

    return web.json_response({'status': 'ok'})
