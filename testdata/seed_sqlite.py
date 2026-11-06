"""
    Desc: creates testdata/demo.db with the same schema as seed_postgres.sql
"""

import sqlite3
from os import remove
from os.path import abspath, dirname, exists, join

PATH = join(dirname(abspath(__file__)), "demo.db")

SQL = """
CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE);
CREATE TABLE categories (id INTEGER PRIMARY KEY, name TEXT NOT NULL, parent_id INTEGER REFERENCES categories (id));
CREATE TABLE products (id INTEGER PRIMARY KEY, category_id INTEGER NOT NULL REFERENCES categories (id), name TEXT NOT NULL);
CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users (id));
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders (id),
    product_id INTEGER NOT NULL REFERENCES products (id),
    UNIQUE (order_id, product_id)
);
CREATE TABLE order_item_notes (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    note TEXT,
    FOREIGN KEY (order_id, product_id) REFERENCES order_items (order_id, product_id)
);
CREATE TABLE audit_log (id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users (id));
CREATE TABLE empty_table (id INTEGER PRIMARY KEY);
"""

if exists(PATH): remove(PATH)

connection = sqlite3.connect(PATH)
connection.executescript(SQL)
connection.close()

print(f"OK. Now: python main.py --url {PATH}")
