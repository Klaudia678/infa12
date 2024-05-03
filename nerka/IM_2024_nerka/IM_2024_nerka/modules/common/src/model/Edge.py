from dataclasses import dataclass, field
from typing import Any

from modules.common.src.model import Node
from modules.common.src.model.EdgeData import EdgeData


@dataclass
class Edge:
    node_a: Node
    node_b: Node
    data: dict[str, Any] = field(init=False, default_factory=lambda: {}, repr=False)
    edge_data: EdgeData = field(init=False, default_factory=lambda: EdgeData(), repr=False)

    def is_same_generation(self, other) -> bool:
        return self.edge_data.generation == other.edge_data.generation

    def get_generation(self):
        return self.edge_data.generation

    def __setitem__(self, key, value):
        if key == 'relative_angle':
            self.edge_data.relative_angle = value
        elif key == 'length':
            self.edge_data.length = value
        elif key == 'mean_thickness':
            self.edge_data.thickness = value
        self.data[key] = value

    def __getitem__(self, key):
        if key == 'relative_angle':
            return self.edge_data.relative_angle
        elif key == 'length':
            return self.edge_data.length
        elif key == 'mean_thickness':
            return self.edge_data.thickness
        return self.data[key]

    def __eq__(self, other) -> bool:
        return (self.node_a == other.node_a and self.node_b == other.node_b) or (
                self.node_a == other.node_b and self.node_b == other.node_a)  # Because graph is not directed order of nodes in edge is unimportant

    def __hash__(self) -> int:
        return hash(self.node_a.__hash__() + self.node_b.__hash__())
