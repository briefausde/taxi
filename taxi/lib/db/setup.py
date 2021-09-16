import logging
from typing import AsyncGenerator

from aiohttp import web
from aiopg.sa import create_engine as async_create_engine

log = logging.getLogger(__name__)


async def setup_database(app: web.Application) -> AsyncGenerator:
    db_engine = await async_create_engine(**app['config']['db'])
    app['db'] = db_engine
    log.info('Connected to database')

    yield

    db_engine.close()
    await db_engine.wait_closed()
    log.info('Disconnected from database')
