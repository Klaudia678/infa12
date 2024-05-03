from dataclasses import dataclass, field
from typing import Any

from modules.common.src.model import Edge


@dataclass(init=True, eq=True, repr=True, unsafe_hash=True)
class Node:
    coords: tuple[int, int, int]
    edges: list[Edge] = field(init=False, default_factory=lambda: [], compare=False)
    data: dict[str, Any] = field(init=False, default_factory=lambda: {}, compare=False)

    def add_edge(self, edge):
        self.edges.append(edge)

    def get_neighbours(self):
        return [e.node_a if e.node_a.coords != self.coords else e.node_b for e in self.edges]

    def copy_without_edges(self):
        copied_node = Node(self.coords)
        copied_node.data = self.data
        return copied_node

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]
