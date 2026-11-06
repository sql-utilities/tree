"""
    Desc: Util to print log(s) to stderr, so stdout stays clean for the result
"""

from sys import stderr

# green color
OK_FORMAT = "\033[92m\033[1m{msg}\033[0m"
# red color
ERR_FORMAT = "\033[91m\033[1m{msg}\033[0m"

def __print(msg: str, formatting: str) -> None:
    log = f"[TREE]: {msg}"
    print(formatting.format(msg=log) if stderr.isatty() else log, file=stderr)

def log_err(msg: str) -> None:
    return __print(msg, ERR_FORMAT)

def log_ok(msg: str) -> None:
    return __print(msg, OK_FORMAT)
