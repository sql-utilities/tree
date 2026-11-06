"""
    Desc: Printer class to render a schema as tree, mermaid or json
"""

import json
import re

from tree.api.graph import Graph
from tree.api.schema import Schema

from tree.api.utils.__logger import log_err

BRANCH_MID = "├── "
BRANCH_LAST = "└── "
INDENT_MID = "│   "
INDENT_LAST = "    "

# mermaid entity name that needs no quotes
IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

class Printer:
    def __frames(self, kids: list, prefix: str) -> list:
        last = len(kids) - 1
        return [(kid, prefix, i == last) for i, kid in reversed(list(enumerate(kids)))]

    def __expand(self, root: str, children: dict, visited: set, lines: list) -> None:
        visited.add(root)
        lines.append(root)

        stack = self.__frames(children.get(root, []), "")
        while stack:
            table, prefix, is_last = stack.pop()
            branch = BRANCH_LAST if is_last else BRANCH_MID

            # table with several parents is expanded once, other places only get a mark
            if table in visited:
                lines.append(f"{prefix}{branch}{table} (↻)")
                continue

            visited.add(table)
            lines.append(f"{prefix}{branch}{table}")
            stack.extend(self.__frames(children.get(table, []), prefix + (INDENT_LAST if is_last else INDENT_MID)))

    def __entity(self, name: str) -> str:
        return name if IDENTIFIER.match(name) else '"' + name.replace('"', "'") + '"'

    def __init__(self, schema: Schema):
        self.schema = schema
        self.graph = Graph(schema)

    def to_tree(self) -> str:
        if not self.schema.tables: return "(no tables)"

        children = self.graph.get_children()
        visited, lines = set(), []

        for root in self.graph.get_roots():
            self.__expand(root, children, visited, lines)

        # tables inside a cycle have no root, so they are printed as extra roots
        for table in sorted(self.schema.tables):
            if table not in visited:
                self.__expand(table, children, visited, lines)

        self_references = self.graph.get_self_references()
        if self_references:
            lines.extend(["", "# self-references:", *[f"{table} (↻)" for table in self_references]])

        return "\n".join(lines)

    def to_mermaid(self) -> str:
        lines, linked = ["erDiagram"], set()

        ordered = sorted(self.schema.foreign_keys, key=lambda fk: (fk.parent_table, fk.child_table, fk.constraint_name))
        for fk in ordered:
            linked.update((fk.parent_table, fk.child_table))
            label = f"{', '.join(fk.parent_columns)} -> {', '.join(fk.child_columns)}".replace('"', "'")
            lines.append(f'    {self.__entity(fk.parent_table)} ||--o{{ {self.__entity(fk.child_table)} : "{label}"')

        lines.extend(f"    {self.__entity(table)}" for table in sorted(self.schema.tables - linked))
        return "\n".join(lines)

    def to_json(self) -> str:
        ordered = sorted(self.schema.foreign_keys, key=lambda fk: (fk.child_table, fk.constraint_name))
        payload = {
            "namespace": self.schema.namespace,
            "tables": sorted(self.schema.tables),
            "foreign_keys": [
                {
                    "constraint_name": fk.constraint_name,
                    "child_table": fk.child_table,
                    "child_columns": list(fk.child_columns),
                    "parent_table": fk.parent_table,
                    "parent_columns": list(fk.parent_columns)
                }
                for fk in ordered
            ]
        }
        return json.dumps(payload, indent=2, ensure_ascii=False)

    def render(self, name: str) -> str | None:
        renderers = {"tree": self.to_tree, "mermaid": self.to_mermaid, "json": self.to_json}

        renderer = renderers.get(name)
        if not renderer: return log_err(f"unknown format '{name}', available: {', '.join(renderers)}")

        return renderer()
