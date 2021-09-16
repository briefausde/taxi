import logging

from aiohttp import web
from aiohttp_swagger import setup_swagger

from taxi.config import get_config
from taxi.lib.db.setup import setup_database
from taxi.lib.metrics.setup import setup_metrics
from taxi.routes import setup_routes

log = logging.getLogger(__name__)


def start_app():
    app = web.Application()

    config = get_config()
    app['config'] = config

    setup_routes(app)

    app.cleanup_ctx.extend([
        setup_database,
        setup_metrics,
    ])

    setup_swagger(app, swagger_url='/api/v1/doc', ui_version=2)

    logging.basicConfig(level=logging.INFO)

    web.run_app(
        app=app,
        host=config['host'],
        port=config['port'],
    )


if __name__ == '__main__':
    start_app()
