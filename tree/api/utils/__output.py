"""
    Desc: Util to print result to stdout in UTF-8 (tree uses box-drawing characters)
"""

from sys import stdout

def write(text: str) -> None:
    if hasattr(stdout, "reconfigure"):
        stdout.reconfigure(encoding="utf-8")
    print(text)
