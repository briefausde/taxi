import asyncio
import logging
from functools import wraps
from typing import Any, Awaitable, Callable

from taxi.lib.metrics.metrics import db_records_count

Coroutine = Callable[..., Awaitable[Any]]

log = logging.getLogger(__name__)


def queries_metric(f: Coroutine):

    @wraps(f)
    async def queries_metric_factory(*args: Any, **kwargs: Any) -> Any:
        db_records_count.inc()
        return await f(*args, **kwargs)
    return queries_metric_factory


def retry(
    *,
    retries: int = 3,
    delay: float = 1,
) -> Callable[..., Coroutine]:

    def retry_factory(f: Coroutine) -> Coroutine:
        @wraps(f)
        async def wrapped(*args: Any, **kwargs: Any) -> Any:
            retry_count = 0
            while True:
                try:
                    if retry_count:
                        log.warning(f'Retry {f.__name__}')
                    return await f(*args, **kwargs)
                except Exception as ex:
                    if retry_count == retries:
                        raise ex
                    else:
                        await asyncio.sleep(delay)
                        retry_count += 1

        return wrapped
    return retry_factory
