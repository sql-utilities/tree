#!/usr/bin/env bash
set -euo pipefail
: "${PG_URL:=postgresql://postgres:postgres@localhost:5432/postgres}"
psql "$PG_URL" -v ON_ERROR_STOP=1 -f "$(dirname "$0")/seed_postgres.sql"
echo "OK. Now: python main.py --url '$PG_URL' --schema sqltree_demo"
