import logging
from json import JSONDecodeError
from types import MappingProxyType
from typing import Any, Dict, Mapping, Optional

from aiohttp.web import Request
from jsonschema import validate, ValidationError
from taxi.lib.exceptions import InvalidBodyError

log = logging.getLogger(__name__)


def immutable_dict(data: Dict[str, Any]) -> Mapping[Any, Any]:
    return MappingProxyType({
        key: immutable_dict(value) if isinstance(value, dict) else value
        for key, value in data.items()})


async def request_to_dict(request: Request) -> dict:
    try:
        return await request.json()
    except JSONDecodeError:
        raise InvalidBodyError("Invalid request body", 400)


async def validate_schema(data: dict, schema: dict) -> dict:
    try:
        validate(data, schema)
        return data
    except ValidationError as e:
        raise InvalidBodyError(e.message, 422)


def as_bool(value: Optional[str]) -> bool:
    if str(value).lower() in ['', '0', 'false', 'none', 'null']:
        return False
    return True
