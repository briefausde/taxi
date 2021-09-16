from aiopg.sa import SAConnection
from aiopg.sa.result import RowProxy

from taxi.models import DriverRoute, RouteDescription
from taxi.bl.utils import Coordinate
from taxi.lib.decorators import retry, queries_metric


@queries_metric
@retry(retries=3, delay=10)
async def insert_driver_route(
    conn: SAConnection,
    driver_id: int,
    coordinate: Coordinate,
    speed: float,
) -> int:
    return await conn.scalar(
        DriverRoute.__table__.insert().values(
            driver_id=driver_id,
            latitude=coordinate.latitude,
            longitude=coordinate.longitude,
            altitude=coordinate.altitude,
            speed=speed,
        )
    )


@queries_metric
@retry(retries=3, delay=10)
async def insert_route_description(
    conn: SAConnection,
    driver_route_id: int,
    description: str,
    is_correct_driver_altitude: bool,
    is_driver_over_speed: bool,
) -> None:
    await conn.scalar(
        RouteDescription.__table__.insert().values(
            driver_route_id=driver_route_id,
            description=description,
            is_correct_driver_altitude=is_correct_driver_altitude,
            is_driver_over_speed=is_driver_over_speed,
        )
    )


@retry(retries=3, delay=10)
async def select_last_driver_route(
    conn: SAConnection,
    driver_id: int,
) -> RowProxy:
    cursor = await conn.execute(
        DriverRoute.__table__.select()
        .where(DriverRoute.driver_id == driver_id)
        .order_by(DriverRoute.date_created.desc())
        .limit(1)
    )
    return await cursor.fetchone() or None
