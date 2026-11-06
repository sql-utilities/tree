"""
    Desc: SqlTree class to initialize other classes
"""

from tree.api.dialect import get_dialect, get_dialects
from tree.api.printer import Printer

from tree.api.utils.__args import get_args
from tree.api.utils.__env import get_env
from tree.api.utils.__json import read
from tree.api.utils.__logger import log_err
from tree.api.utils.__output import write

class SqlTree:
    def __detect(self, url: str) -> str:
        # postgres DSN or a path to a file
        return "postgres" if url.startswith(("postgres://", "postgresql://")) else "sqlite"

    def __init__(self):
        # 0 - success, 1 - failed
        self.status = 1

        try:
            settings = read("settings") or {}
            args = get_args(settings, get_dialects())

            self.__url = args["url"] or get_env("DATABASE_URL")
            if not self.__url: return log_err("missing database url: use --url or set DATABASE_URL in tokens.env")

            self.__db = self.__detect(self.__url) if args["db"] == "auto" else args["db"]

            self.dialect = get_dialect(self.__db)
            if not self.dialect: return

            self.schema = self.dialect.introspect(self.__url, args["schema"])
            if not self.schema: return
            if not self.schema.tables: return log_err(f"no tables found in schema '{args['schema']}'")

            self.printer = Printer(self.schema)

            self.output = self.printer.render(args["format"])
            if self.output is None: return

            write(self.output)
            self.status = 0
        except Exception as err:
            log_err(f"failed to start: {err}")
