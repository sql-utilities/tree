"""
    Desc: Util to read .json file(s)
"""

from json import load, JSONDecodeError
from os.path import abspath, dirname, join, normpath

from tree.api.utils.__logger import log_err

# returns a correct path to tree/config directory
CONFIG_DIRECTORY = normpath(join(dirname(abspath(__file__)), "..", "..", "config"))

def read(name: str) -> dict | list | None:
    try:
        file_path = join(CONFIG_DIRECTORY, f"{name}.json")
        with open(file_path, "r", encoding="utf-8") as file:
            return load(file)
    except (JSONDecodeError, FileNotFoundError) as err:
        return log_err(err)
