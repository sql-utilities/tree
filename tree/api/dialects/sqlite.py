"""
    Desc: SQLite class to read tables and foreign keys from a .db file via PRAGMA
"""

import sqlite3
from os.path import isfile
from pathlib import Path

from tree.api.dialect import Dialect, register
from tree.api.schema import ForeignKey, Schema

from tree.api.utils.__logger import *

PREFIX = "sqlite:///"

def quote(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'

@register("sqlite")
class SQLite(Dialect):
    def __primary_key(self, connection: sqlite3.Connection, table: str) -> list:
        rows = connection.execute(f"PRAGMA table_info({quote(table)})").fetchall()
        # pk is 1-based position, 0 means not a key
        return [row[1] for row in sorted((row for row in rows if row[5]), key=lambda row: row[5])]

    def __foreign_keys(self, connection: sqlite3.Connection, table: str) -> list:
        grouped = {}
        for fk_id, _, parent, child_column, parent_column, *_ in connection.execute(f"PRAGMA foreign_key_list({quote(table)})"):
            _, child_columns, parent_columns = grouped.setdefault(fk_id, (parent, [], []))
            child_columns.append(child_column)
            parent_columns.append(parent_column)

        result = []
        for fk_id, (parent, child_columns, parent_columns) in grouped.items():
            # "REFERENCES parent" without columns points to the primary key of the parent
            if not all(parent_columns):
                parent_columns = self.__primary_key(connection, parent) or parent_columns
            # SQLite has no constraint names, so a stable one is generated
            result.append(ForeignKey(table, tuple(child_columns), parent, tuple(parent_columns), f"{table}_fk{fk_id}"))
        return result

    def introspect(self, url: str, namespace: str) -> Schema | None:
        path = url[len(PREFIX):] if url.startswith(PREFIX) else url
        if not isfile(path): return log_err(f"SQLite file not found: {path}")

        connection = None
        try:
            connection = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)
            with connection:
                rows = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'").fetchall()
                tables = {row[0] for row in rows}
                foreign_keys = [fk for table in sorted(tables) for fk in self.__foreign_keys(connection, table)]
        except sqlite3.DatabaseError as err:
            return log_err(f"SQLite error: {err}")
        finally:
            if connection is not None:
                connection.close()

        log_ok(f"opened SQLite file: {path}")
        return Schema(tables=tables, foreign_keys=foreign_keys, namespace="main")
