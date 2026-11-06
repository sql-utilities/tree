<div align="center">

[![Python](https://img.shields.io/badge/language-Python-60a5fa?style=flat-square)]()
[![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-4ade80?style=flat-square)]()
[![SQLite](https://img.shields.io/badge/database-SQLite-fbbf24?style=flat-square)]()
[![Output](https://img.shields.io/badge/output-tree%20%7C%20mermaid%20%7C%20json-a87ef5?style=flat-square)]()

</div>

SqlTree reads a PostgreSQL or SQLite schema and prints a tree of tables by foreign keys. It handles composite keys, self-references, tables with several parents and cycles, and renders the result as a text tree, a Mermaid `erDiagram` or JSON.

Instead of reading `information_schema` by hand and drawing relations yourself, you drop one config value and call `SqlTree()`. Everything else is handled for you.

```
database ──► dialect (postgres / sqlite) ──► graph ──► printer ──► stdout
```

---

## Example

`main.py`

```python
from sys import exit

from tree import SqlTree

exit(SqlTree().status)
```

```
python main.py --url shop.db                                                     # SQLite file, no server needed
python main.py --url "postgresql://user:pass@localhost:5432/db" --schema public  # PostgreSQL
```

The dialect is detected by the url: `postgres://` and `postgresql://` mean PostgreSQL, anything else is a path to a SQLite file (`sqlite:///path` also works). Use `--db postgres|sqlite` to set it explicitly.

```
categories
└── products
    └── order_items
        └── order_item_notes
empty_table
users
├── audit_log
└── orders
    └── order_items (↻)

# self-references:
categories (↻)
```

Other formats:

```
python main.py --url "$PG_URL" --schema sqltree_demo --format mermaid
python main.py --url "$PG_URL" --schema sqltree_demo --format json
```

Logs go to `stderr`, the result goes to `stdout`, so `--format json | jq` always gets clean JSON. The exit code is `0` on success and `1` on failure.

### How to read the tree

- **Root** is a table without outgoing foreign keys (self-reference does not count). **Children** are tables that reference it.
- A table with several parents is expanded once (roots and children are walked alphabetically). Every other place gets a `(↻)` mark.
- Tables inside a cycle have no root, so they are printed as extra roots and never loop the walk.
- Self-references are printed in a separate `# self-references:` block.

---

## Configuration

`sqltree/config/settings.json` — defaults, any of them can be overridden by a command line argument:

```json
{
    "db": "auto",
    "schema": "public",
    "format": "tree"
}
```

`sqltree/config/tokens.env` — secrets, never commit:

```
DATABASE_URL=postgresql://user:pass@localhost:5432/db
```

`--url` wins over `DATABASE_URL`. `--schema` is used by PostgreSQL only. With `DATABASE_URL` set you can just run `python main.py`.

---

## Requirements

- Python `3.10+`
- SQLite works out of the box, PostgreSQL needs a running server (other databases can be added as dialects)

```
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Test database

SQLite, no server needed:

```
python testdata/seed_sqlite.py                      # creates testdata/demo.db
python main.py --url testdata/demo.db               # compare with testdata/expected_tree.txt
```

PostgreSQL:

```
chmod +x testdata/seed_postgres.sh
export PG_URL="postgresql://postgres:postgres@localhost:5432/postgres"
bash testdata/seed_postgres.sh
python main.py --url "$PG_URL" --schema sqltree_demo      # compare with testdata/expected_tree.txt
```

The script is idempotent: every run recreates the `sqltree_demo` schema. `psql` must be installed.

---

## Project structure

```
sqltree/
├── config/
│   ├── tokens.env          ← secrets, never commit
│   └── settings.json       ← default dialect, schema and format
├── api/
│   ├── dialect.py          ← Dialect base class + registry
│   ├── dialects/
│   │   ├── postgres.py     ← information_schema
│   │   └── sqlite.py       ← PRAGMA foreign_key_list
│   ├── schema.py           ← ForeignKey, Schema
│   ├── graph.py            ← parent -> children map, roots
│   ├── printer.py          ← tree / mermaid / json
│   └── utils/
│       ├── __args.py
│       ├── __env.py
│       ├── __json.py
│       ├── __logger.py
│       └── __output.py
└── __init__.py             ← SqlTree() entrypoint
```

## Adding a dialect

1. Create `sqltree/api/dialects/mysql.py`:

```python
from tree.api.dialect import Dialect, register
from tree.api.schema import ForeignKey, Schema

from tree.api.utils.__logger import *


@register("mysql")
class MySQL(Dialect):
    def introspect(self, url: str, namespace: str) -> Schema | None:
        try:
            import pymysql
        except ImportError:
            return log_err("pymysql is not installed")

        # read tables and foreign keys, then:
        return Schema(tables=tables, foreign_keys=[ForeignKey(...)], namespace=namespace)
```

2. Add one import line to `sqltree/api/dialects/__init__.py`:

```python
from tree.api.dialects import mysql
```

3. Add the driver to `requirements.txt`.

After that `python main.py --db mysql --url ...` works. Core classes stay untouched.

## Limitations

- Both databases are opened read-only. PostgreSQL is read via `information_schema`, SQLite via `PRAGMA`.
- SQLite has no constraint names, so they are generated as `<table>_fk<n>`.
- Foreign keys to tables of another schema are ignored.
- A foreign key that references a unique index without a constraint is not visible in `information_schema`.
- Constraint names in PostgreSQL are unique per table only. With equal names in one schema `information_schema` may mismatch columns (generated `<table>_<col>_fkey` names are safe).

## Contributing

Contributions are welcome. If you find a bug, have a feature idea, or want to improve the docs, feel free to open an issue or a pull request.

- **Keep it small.** SqlTree is intentionally minimal. New features should solve a clear problem that can't already be handled by a dialect or a config value.
- **Match the style.** Use the `__` prefix for private methods and attributes, keep utilities in `sqltree/api/utils/`, and follow the existing class-per-responsibility pattern.
- **One thing per PR.** Focused pull requests are easier to review and faster to merge.
# tree
# tree
# tree
# tree
# tree
