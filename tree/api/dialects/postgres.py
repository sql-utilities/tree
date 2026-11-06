"""
    Desc: Postgres class to read tables and foreign keys via information_schema
"""

from tree.api.dialect import Dialect, register
from tree.api.schema import ForeignKey, Schema

from tree.api.utils.__logger import *

TABLES_SQL = """
SELECT table_name
FROM information_schema.tables
WHERE table_type = 'BASE TABLE' AND table_schema = %s
ORDER BY table_name
"""

# parent columns are matched by position_in_unique_constraint, so composite keys keep their column order
FOREIGN_KEYS_SQL = """
SELECT kcu.constraint_name,
       kcu.table_name   AS child_table,
       kcu.column_name  AS child_column,
       ref.table_name   AS parent_table,
       ref.column_name  AS parent_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON kcu.constraint_schema = tc.constraint_schema
 AND kcu.constraint_name = tc.constraint_name
 AND kcu.table_name = tc.table_name
JOIN information_schema.referential_constraints rc
  ON rc.constraint_schema = tc.constraint_schema
 AND rc.constraint_name = tc.constraint_name
JOIN information_schema.key_column_usage ref
  ON ref.constraint_schema = rc.unique_constraint_schema
 AND ref.constraint_name = rc.unique_constraint_name
 AND ref.ordinal_position = kcu.position_in_unique_constraint
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = %s
  AND ref.table_schema = tc.table_schema
ORDER BY kcu.table_name, kcu.constraint_name, kcu.ordinal_position
"""

@register("postgres")
class Postgres(Dialect):
    def __group(self, rows: list) -> list:
        grouped = {}
        for constraint, child, child_column, parent, parent_column in rows:
            _, child_columns, parent_columns = grouped.setdefault((child, constraint), (parent, [], []))
            child_columns.append(child_column)
            parent_columns.append(parent_column)

        return [
            ForeignKey(child, tuple(child_columns), parent, tuple(parent_columns), constraint)
            for (child, constraint), (parent, child_columns, parent_columns) in grouped.items()
        ]

    def introspect(self, url: str, namespace: str) -> Schema | None:
        try:
            import psycopg
        except ImportError:
            return log_err("psycopg is not installed, run: pip install -r requirements.txt")

        try:
            with psycopg.connect(url) as connection:
                connection.read_only = True
                with connection.cursor() as cursor:
                    cursor.execute(TABLES_SQL, (namespace,))
                    tables = {row[0] for row in cursor.fetchall()}

                    cursor.execute(FOREIGN_KEYS_SQL, (namespace,))
                    rows = cursor.fetchall()
        except psycopg.Error as err:
            return log_err(f"PostgreSQL error: {str(err).splitlines()[0]}")

        log_ok(f"connected to the database, schema: {namespace}")
        return Schema(tables=tables, foreign_keys=self.__group(rows), namespace=namespace)
