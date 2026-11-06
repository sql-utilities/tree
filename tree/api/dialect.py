"""
    Desc: Dialect base class and registry to support different database(s)
"""

from abc import ABC, abstractmethod
from typing import Callable

from tree.api.schema import Schema
from tree.api.utils.__logger import log_err

# registered dialect(s), filled by @register
DIALECTS: dict = {}

class Dialect(ABC):
    @abstractmethod
    def introspect(self, url: str, namespace: str) -> Schema | None:
        """Connects to the database and returns its tables and foreign keys"""

def register(name: str) -> Callable:
    def decorator(cls: type) -> type:
        DIALECTS[name] = cls
        return cls
    return decorator

def load() -> None:
    # importing the package registers all built-in dialect(s)
    import tree.api.dialects

def get_dialects() -> list:
    load()
    return sorted(DIALECTS)

def get_dialect(name: str) -> Dialect | None:
    load()
    dialect = DIALECTS.get(name)
    if not dialect: return log_err(f"unknown dialect '{name}', available: {', '.join(sorted(DIALECTS))}")
    return dialect()
