import logging
import os
import sys
from typing import Any, Dict, Optional

import trafaret as t
from trafaret_config import ConfigError
from trafaret_config import read_and_validate


log = logging.getLogger(__name__)

CONFIG_FILE_NAME = 'settings.json'

DB_TRAFARET = t.Dict({
    'host': t.String(),
    'port': t.Int(),
    'database': t.String(),
    'user': t.String(),
    'password': t.String(),
    'minsize': t.Int(),
    'maxsize': t.Int(),
})

APP_CONFIG_TRAFARET = t.Dict({
    'db': DB_TRAFARET,
    'metrics_port': t.Int(),
    'host': t.String(),
    'port': t.Int(),
})


def read_app_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    filename = config_path or os.environ['CONFIG_PATH']
    return read_and_validate_config(filename)


def read_and_validate_config(filename: str) -> Dict[str, Any]:
    try:
        config = read_and_validate(filename, APP_CONFIG_TRAFARET)
    except ConfigError as e:
        for error_message in e.errors:
            log.error(str(error_message))
        sys.exit(1)

    log.info(f'Config from {filename}')
    return config


def get_config() -> Dict[str, Any]:
    return read_app_config(CONFIG_FILE_NAME)
