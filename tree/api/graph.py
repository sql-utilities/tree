"""
    Desc: Graph class to build parent -> children map from foreign key(s)
"""

from tree.api.schema import Schema

class Graph:
    def __init__(self, schema: Schema):
        self.schema = schema

        # self-references and keys to unknown tables are not edges
        self.__edges = [
            fk for fk in schema.foreign_keys
            if fk.child_table != fk.parent_table
            and fk.child_table in schema.tables
            and fk.parent_table in schema.tables
        ]

    def get_children(self) -> dict:
        children = {}
        for fk in self.__edges:
            children.setdefault(fk.parent_table, set()).add(fk.child_table)
        return {parent: sorted(kids) for parent, kids in children.items()}

    def get_roots(self) -> list:
        with_parents = {fk.child_table for fk in self.__edges}
        return sorted(self.schema.tables - with_parents)

    def get_self_references(self) -> list:
        return sorted({
            fk.child_table for fk in self.schema.foreign_keys
            if fk.child_table == fk.parent_table and fk.child_table in self.schema.tables
        })
