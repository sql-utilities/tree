"""
    Desc: Util to read command line argument(s), defaults come from settings.json
"""

from argparse import ArgumentParser

VERSION = "0.1.0"
FORMATS = ["tree", "mermaid", "json"]

def get_args(settings: dict, dialects: list) -> dict:
    parser = ArgumentParser(prog="tree", description="Prints a tree of tables by foreign keys.")

    parser.add_argument("--url", default=None, help="postgres DSN or path to a SQLite file, falls back to DATABASE_URL from tokens.env")
    parser.add_argument("--schema", default=settings.get("schema", "public"), help="schema, used by postgres only (default: public)")
    parser.add_argument("--format", choices=FORMATS, default=settings.get("format", "tree"), help="output format (default: tree)")
    parser.add_argument("--db", default=settings.get("db", "auto"), help=f"dialect (default: auto, by url), available: {', '.join(dialects)}")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")

    return vars(parser.parse_args())
