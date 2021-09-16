from typing import Any

from prometheus_client import Counter
from prometheus_client.metrics import MetricWrapperBase

APP_PREFIX = 'taxi'


def create_metric(
    metric: MetricWrapperBase,
    name: str,
    *args: Any,
    **kw: Any
) -> MetricWrapperBase:
    return metric(f'{APP_PREFIX}_{name}', *args, **kw)


db_records_count = create_metric(
    Counter,
    'db_records_count',
    'Records in database',
    [],
)

unique_drivers_count = create_metric(
    Counter,
    'unique_drivers_count',
    'Unique drivers count',
    [],
)

over_speed_drivers_count = create_metric(
    Counter,
    'over_speed_drivers_count',
    'Over speed drivers count',
    [],
)

coordinates_count = create_metric(
    Counter,
    'coordinates_count',
    'Coordinates count',
    [],
)

invalid_altitude_count = create_metric(
    Counter,
    'invalid_altitude_count',
    'Invalid driver altitude_count',
    [],
)
