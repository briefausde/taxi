import logging
from typing import AsyncGenerator

from aiohttp import web
from prometheus_async.aio.web import start_http_server

log = logging.getLogger(__name__)


async def setup_metrics(app: web.Application) -> AsyncGenerator:
    app['metrics_server'] = await start_http_server(
        port=app['config']['metrics_port']
    )
    log.info('Metrics server started')

    yield

    await app['metrics_server'].close()
    log.info('Metrics server stopped')
