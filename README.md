<h1 align="center">tree</h1>

<p align="center"><em>Read a SQL schema, print a tree of tables by foreign keys</em></p>

<div align="center">

[![Documentation](https://img.shields.io/badge/docs-online-4ade80?style=flat-square)](https://example.com/tree/docs/)
[![Python](https://img.shields.io/badge/language-Python-60a5fa?style=flat-square)]()
[![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-f87171?style=flat-square)]()
[![SQLite](https://img.shields.io/badge/database-SQLite-a87ef5?style=flat-square)]()

</div>

---

tree reads a PostgreSQL or SQLite schema and prints a tree of tables by foreign keys. It handles composite keys, self-references, tables with several parents and cycles, and renders the result as a text tree, a Mermaid `erDiagram` or JSON.

Instead of reading `information_schema` by hand and drawing relations yourself, you pass one URL and call `SqlTree()`. The dialect is detected from the URL, the rest is handled for you.

---

## Example

`main.py`

```python
from sys import exit

from tree import SqlTree

exit(SqlTree().status)
```

```bash
python main.py --url shop.db                                                     # SQLite file, no server needed
python main.py --url "postgresql://user:pass@localhost:5432/db" --schema public  # PostgreSQL
```

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

```bash
python main.py --url "$PG_URL" --schema tree_demo --format mermaid
python main.py --url "$PG_URL" --schema tree_demo --format json
```

Logs go to `stderr`, the result goes to `stdout`, so `--format json | jq` always gets clean JSON. The exit code is `0` on success and `1` on failure.

### How to read the tree

- **Root** is a table without outgoing foreign keys (self-reference does not count). **Children** are tables that reference it.
- A table with several parents is expanded once (roots and children are walked alphabetically). Every other place gets a `(↻)` mark.
- Tables inside a cycle have no root, so they are printed as extra roots and never loop the walk.
- Self-references are printed in a separate `# self-references:` block.

---

## Configuration

`tree/config/settings.json` — defaults, any of them can be overridden by a command line argument:

```json
{
    "db": "auto",
    "schema": "public",
    "format": "tree"
}
```

`tree/config/tokens.env` — secrets, never commit:

```
DATABASE_URL=postgresql://user:pass@localhost:5432/db
```

`--url` wins over `DATABASE_URL`. `--schema` is used by PostgreSQL only. With `DATABASE_URL` set you can just run `python main.py`.

The dialect is detected by the URL: `postgres://` and `postgresql://` mean PostgreSQL, anything else is a path to a SQLite file (`sqlite:///path` also works). Use `--db postgres|sqlite` to set it explicitly.

---

## Requirements

- Python `3.10+`
- SQLite works out of the box, PostgreSQL needs a running server (other databases can be added as dialects)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Test database

SQLite, no server needed:

```bash
python testdata/seed_sqlite.py                      # creates testdata/demo.db
python main.py --url testdata/demo.db               # compare with testdata/expected_tree.txt
```

PostgreSQL:

```bash
chmod +x testdata/seed_postgres.sh
export PG_URL="postgresql://postgres:postgres@localhost:5432/postgres"
bash testdata/seed_postgres.sh
python main.py --url "$PG_URL" --schema tree_demo   # compare with testdata/expected_tree.txt
```

The script is idempotent: every run recreates the `tree_demo` schema. `psql` must be installed.

---

## Project structure

```
tree/
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

---

## Adding a dialect

1. Create `tree/api/dialects/mysql.py`:

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

2. Add one import line to `tree/api/dialects/__init__.py`:

```python
from tree.api.dialects import mysql
```

3. Add the driver to `requirements.txt`.

After that `python main.py --db mysql --url ...` works. Core classes stay untouched.

---

## Limitations

- Both databases are opened read-only. PostgreSQL is read via `information_schema`, SQLite via `PRAGMA`.
- SQLite has no constraint names, so they are generated as `<table>_fk<n>`.
- Foreign keys to tables of another schema are ignored.
- A foreign key that references a unique index without a constraint is not visible in `information_schema`.
- Constraint names in PostgreSQL are unique per table only. With equal names in one schema `information_schema` may mismatch columns (generated `<table>_<col>_fkey` names are safe).

---

## Contributing

Contributions are welcome — open an issue or PR.

- **Keep it small.** tree is intentionally minimal. New features should solve a problem that can't be fixed by a dialect or a config value.
- **Match the style.** `__` for private members, utilities in `tree/api/utils/`, one class per responsibility.
- **One thing per PR.** Focused PRs merge faster.

If you're unsure whether an idea fits, open an issue first.

---

<p align="center"><sub>
<a href="https://example.com/tree/docs/">Docs</a> ·
<a href="https://github.com/example/tree/issues">Issues</a> ·
<a href="https://github.com/example/tree/releases">Releases</a>
</sub></p>