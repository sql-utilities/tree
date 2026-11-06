DROP SCHEMA IF EXISTS sqltree_demo CASCADE;
CREATE SCHEMA sqltree_demo;
SET search_path = sqltree_demo;

CREATE TABLE users (
    id    integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email text NOT NULL UNIQUE
);

CREATE TABLE categories (
    id        integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name      text NOT NULL,
    parent_id integer REFERENCES categories (id)
);

CREATE TABLE products (
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_id integer NOT NULL REFERENCES categories (id),
    name        text NOT NULL
);

CREATE TABLE orders (
    id      integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id integer NOT NULL REFERENCES users (id)
);

CREATE TABLE order_items (
    id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id   integer NOT NULL REFERENCES orders (id),
    product_id integer NOT NULL REFERENCES products (id),
    UNIQUE (order_id, product_id)
);

CREATE TABLE order_item_notes (
    id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id   integer NOT NULL,
    product_id integer NOT NULL,
    note       text,
    FOREIGN KEY (order_id, product_id) REFERENCES order_items (order_id, product_id)
);

CREATE TABLE audit_log (
    id      integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id integer REFERENCES users (id)
);

CREATE TABLE empty_table (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY
);
