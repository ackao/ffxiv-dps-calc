"""Custom types for columns"""

from sqlalchemy.types import TypeDecorator, Integer
from sqlalchemy.engine.interfaces import Dialect
from typing import Optional


class HexColor(TypeDecorator):
    """Sets a hex type that's stored as an integer in the db but returned as a string"""
    impl = Integer
    cache_ok = True

    def process_bind_param(self, value: Optional[str], dialect: Dialect) -> Optional[int]:
        if value.startswith('#'):
            return int(value[1:], 16)
        return int(value, 16)

    def process_result_value(self, value: Optional[int], dialect: Dialect) -> Optional[str]:
        return hex(value)[2:]
