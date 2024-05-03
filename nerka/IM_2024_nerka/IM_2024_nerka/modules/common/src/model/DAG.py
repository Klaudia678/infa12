import pickle
import queue
from copy import deepcopy
from functools import cache
from typing import Any

import numpy as np
from typing_extensions import Self

from modules.common.src.app_utils.Logger import get_logger
from modules.common.src.model.VolumeData import VolumeData
from modules.common.src.model import Node, Edge

from abc import abstractmethod

from modules.common.src.model import Edge


class AbstractTraverseListener:

    @abstractmethod
    def on_edge_traversed(self, parent_edge: Edge, edge: Edge):
        pass


class DAG:
    def __init__(self, root: Node, volume_shape: VolumeData, nodes: list[Node], edges: list[Edge]):
        self.id = ''
        self.root = root
        self.nodes = nodes
        self.edges = edges
        self.volume_shape = volume_shape
        self.data = {}

    def get_coords_node_dict(self) -> dict[tuple, Node]:
        return {xyz.coords: xyz for xyz in self.nodes}

    def remove_node(self, node: Node) -> None:
        if node not in self.nodes:
            get_logger().warning(f'Node {node} is not part of DAG, hence cannot be removed')
            return
        if len(node.edges) > 2:
            get_logger().warning(f'Node {node} has {len(node.edges)} edges hence cannot be removed')
            raise NotImplementedError('Not yet implemented')
        # TODO: removing node

    def get_edge(self, param_edge: Edge) -> Edge:
        for edge in self.edges:
            if edge == param_edge:
                return edge

    @cache
    def get_nodes_by_level(self, level: int) -> list[Node]:
        node_list: list[Node] = []
        for node in self.nodes:
            if len(node.edges) == level:
                node_list.append(node)
        return node_list

    @cache
    def get_generation_node_dict(self) -> dict[int, list[Node]]:
        generation_to_node_dict: dict[int, list[Node]] = {}

        class Listener(AbstractTraverseListener):
            def on_edge_traversed(self, parent_edge: Edge, edge: Edge):
                if parent_edge is None:
                    generation_to_node_dict[0] = [edge.node_a]
                else:
                    generation = parent_edge.get_generation()
                    if generation not in generation_to_node_dict.keys():
                        generation_to_node_dict[generation] = []
                    generation_to_node_dict[generation].append(edge.node_a)

        self.traverse_from_root(Listener())
        return generation_to_node_dict

    @cache
    def get_number_of_full_levels(self) -> int:
        full: int = 0
        all_full: bool = True
        generation_node_dict = self.get_generation_node_dict()
        for key, value in generation_node_dict.items():
            if pow(2, key) == len(value) and all_full:
                full += 1
            else:
                all_full = False
        return full

    def get_nodes_between_generations(self, generation_one: int, generation_two: int) -> list[Node]:
        node_list = []
        generation_node_dict = self.get_generation_node_dict()
        for generation in range(generation_one - 1, generation_two - 1):
            node_list += generation_node_dict[generation]
        return node_list

    def traverse_from_root(self, traverse_listener: AbstractTraverseListener, max_generation=np.inf):
        q = queue.Queue()
        q.put((None, self.root))
        while not q.empty():
            parent_edge, node = q.get()
            for edge in node.edges:
                traverse_listener.on_edge_traversed(parent_edge, edge)
                if edge.edge_data.generation < max_generation:
                    q.put((edge, edge.node_b))

    def get_edges_by_parameter(self, parameter_name: str, parameter_value: Any) -> list:
        ret = [x for x in self.edges if x[parameter_name] == parameter_value]
        get_logger().debug(f'Numer of filtered edges {len(ret)}')
        return ret

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]

    def get_parameters(self) -> dict:
        return self.data

    def save(self, filename: str):
        with open(filename, 'wb') as output:
            pickle.dump(self, output)

    def get_shape(self) -> tuple:
        shape = (0, 0, 0)
        for node in self.nodes:
            shape = get_max_coords(node.coords, shape)
        shape = tuple(map(lambda x, y: x + y, shape, (1, 1, 1)))
        return shape

    def get_structure_copy(self) -> Self:
        dag = deepcopy(self)
        dag.data = {}
        for edge in dag.edges:
            edge.data = {}
        for node in dag.nodes:
            node.data = {}
        return dag


def get_max_coords(max_coords: tuple, new_coords: tuple) -> tuple:
    coord_list = []
    for new_coord, max_coord in zip(max_coords, new_coords):
        coord_list.append(max(new_coord, max_coord))
    return tuple(coord_list)
