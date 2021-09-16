from typing import List, Union


class InvalidBodyError(Exception):
    def __init__(self, errors: Union[str, List], status: int) -> None:
        self.errors = errors
        self.status = status
