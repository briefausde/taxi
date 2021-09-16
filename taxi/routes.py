from aiohttp import web

from taxi.controllers.private import healthcheck
from taxi.controllers.public import handle_driver_data


def setup_routes(app: web.Application) -> None:
    app.add_routes([web.get('/healthcheck', healthcheck)])
    app.add_routes([web.post('/handle_driver_data', handle_driver_data)])
