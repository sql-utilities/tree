"""
    Desc: ForeignKey and Schema classes to store data read from a database
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class ForeignKey:
    child_table: str
    child_columns: tuple
    parent_table: str
    parent_columns: tuple
    constraint_name: str

@dataclass
class Schema:
    tables: set
    foreign_keys: list
    namespace: str | None = None
