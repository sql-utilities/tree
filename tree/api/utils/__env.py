"""
    Desc: Util to access .env file(s)
"""

from os import getenv
from dotenv import load_dotenv
from os.path import abspath, dirname, join, normpath

# returns a correct path to tree/config/tokens.env file
ENV_PATH = normpath(join(dirname(abspath(__file__)), "..", "..", "config", "tokens.env"))

load_dotenv(dotenv_path=ENV_PATH)

def get_env(name: str) -> str | None:
    return getenv(name) or None
