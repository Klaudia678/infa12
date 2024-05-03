import numpy as np
from skimage import morphology
from skimage.draw import line_nd

from modules.common.src.visualization.ColorMapVisualizer import ColorMapVisualizer
from modules.common.src.visualization.VolumeVisualizer import VolumeVisualizer
from modules.common.src.model import DAG
from modules.common.src.model.VolumeData import VolumeData


# TODO: Major refactoring

def visualize_dag(dag: DAG, edge_size='mean_thickness', fixed_node_size: int = 0, edges_to_highlight=None) -> None:
    visualize_lsd(get_dag_visualisation(dag, edge_size, fixed_node_size, edges_to_highlight))


def get_dag_visualisation(dag: DAG, edge_size='mean_thickness', fixed_node_size: int = 0, edges_to_highlight=None) -> VolumeData:
    if edges_to_highlight is None:
        edges_to_highlight = []
    visualization = np.zeros(dag.get_shape())

    visualization = draw_nodes(visualization, dag.nodes, fixed_node_size)
    visualization = draw_edges(visualization, dag.edges, edge_size=edge_size, edges_to_highlight=edges_to_highlight)
    return visualization


def draw_nodes(image, nodes, value):
    nodes_image = __print_kernels(image, nodes, value)
    return nodes_image


def draw_directions(image, edges, start_value=2, end_value=3, length=10):
    image = image.copy()

    for edge in edges:
        start_point = edge.node_a['centroid']
        end_point = start_point + length * edge['start_direction']
        end_point = np.maximum([0, 0, 0], end_point)
        end_point = np.minimum(np.array(image.shape) - 1, end_point)
        image[line_nd(start_point, end_point)] = start_value

        start_point = edge.node_b['centroid']
        end_point = start_point + length * edge['end_direction']
        end_point = np.maximum([0, 0, 0], end_point)
        end_point = np.minimum(np.array(image.shape) - 1, end_point)
        image[line_nd(start_point, end_point)] = end_value

    return image


def __print_kernels(image, nodes, value):
    image = image.copy()
    max_kernel_radius = int(max([node['thickness'] for node in nodes]))
    kernels = [__spherical_kernel(radius) for radius in range(max_kernel_radius + 1)]

    padded_image = np.pad(image, max_kernel_radius)
    kernels_image = np.zeros(padded_image.shape)

    for node in nodes:
        x, y, z = (coord + max_kernel_radius for coord in node.coords)
        if value != 0:
            kernel_radius = value
        else:
            kernel_radius = int(node['thickness'])
        kernel = kernels[kernel_radius]

        mask_slice = kernels_image[
                     x - kernel_radius:x + kernel_radius + 1,
                     y - kernel_radius:y + kernel_radius + 1,
                     z - kernel_radius:z + kernel_radius + 1
                     ]

        mask_slice[:] = np.logical_or(mask_slice, kernel)

    kernels_image = kernels_image[
                    max_kernel_radius:-max_kernel_radius,
                    max_kernel_radius:-max_kernel_radius,
                    max_kernel_radius:-max_kernel_radius
                    ]

    image[kernels_image == 1] = value
    return image


def __spherical_kernel(outer_radius, thickness=1, filled=True):
    outer_sphere = morphology.ball(radius=outer_radius)
    if filled:
        return outer_sphere

    thickness = min(thickness, outer_radius)

    inner_radius = outer_radius - thickness
    inner_sphere = morphology.ball(radius=inner_radius)

    begin = outer_radius - inner_radius
    end = begin + inner_sphere.shape[0]
    outer_sphere[begin:end, begin:end, begin:end] -= inner_sphere
    return outer_sphere


def draw_edges(image, edges, edge_size: any = 'mean_thickness', interpolate=True, edges_to_highlight=None):  # TODO: Make edge_size be size not color
    image = image.copy()
    for i, edge in enumerate(edges):
        if edges_to_highlight is not None and edge in edges_to_highlight:
            fill_value = 50
        elif type(edge_size) is str:
            fill_value = edge[edge_size]
        else:
            fill_value = edge_size

        if interpolate:
            image[line_nd(edge.node_a.coords, edge.node_b.coords)] = fill_value
        else:
            for v in edge['voxels']:
                image[tuple(v)] = fill_value

    return image


def draw_central_line(image, dag):
    image_with_edges = draw_edges(image, dag.edges, edge_size=1, interpolate=False)
    for n in dag.nodes:
        for v in n['voxels']:
            image_with_edges[tuple(v)] = 1

    return image_with_edges


def visualize_addition(partial, full):
    partial = (partial.copy() > 0).astype(np.uint8)
    addition = (full > 0).astype(np.uint8)
    addition[partial == 1] = 0
    ColorMapVisualizer(partial + addition * 4).visualize()


def visualize_skeleton(skeleton, mask):
    skel = (skeleton > 0).astype(np.uint8) * 4
    mask = (mask > 0).astype(np.uint8) * 3
    mask[skeleton != 0] = 0
    ColorMapVisualizer(skel + mask).visualize()


def visualize_lsd(lsd_mask):
    ColorMapVisualizer(lsd_mask.astype(np.uint8)).visualize()


def visualize_marked_voxels(background: np.ndarray, marked_voxels: np.ndarray[tuple], voxel_radius: int = 10,
                            color_function: callable = None) -> None:
    if isinstance(voxel_radius, int):
        voxel_radius = np.full(marked_voxels.shape[0], voxel_radius)
    if color_function is None:
        def funct(voxel: tuple) -> int: return 4

        color_function = funct
    visualisation = np.zeros(background.shape)
    visualisation[background > 0] = 1
    for marked_voxel, mark_radius in zip(marked_voxels, voxel_radius):
        x, y, z = tuple(marked_voxel)
        visualisation[x - mark_radius: x + mark_radius, y - mark_radius: y + mark_radius, z - mark_radius: z + mark_radius] = color_function(marked_voxel)
    visualize_lsd(visualisation)


def visualize_gradient(lsd_mask):
    ColorMapVisualizer(lsd_mask.astype(np.uint8)).visualize(gradient=True)


def visualize_mask_non_bin(mask):
    VolumeVisualizer((mask > 0).astype(np.uint8) * 255, binary=False).visualize()


def visualize_mask_bin(mask):
    VolumeVisualizer((mask > 0).astype(np.uint8), binary=True).visualize()


def draw_graph(graph: DAG):
    mask = np.zeros(graph.get_shape(), dtype=np.uint8)
    for edge in graph.edges:
        node1, node2 = edge.node_a, edge.node_b
        x1, y1, z1 = node1.coords
        x2, y2, z2 = node2.coords
        line_x = np.linspace(x1, x2, num=300, endpoint=True, dtype=np.int32)
        line_y = np.linspace(y1, y2, num=300, endpoint=True, dtype=np.int32)
        line_z = np.linspace(z1, z2, num=300, endpoint=True, dtype=np.int32)
        for i in range(len(line_x)):
            mask[line_x[i], line_y[i], line_z[i]] = 255

    for node in graph.nodes:
        x, y, z = node.coords
        mask[x, y, z] = 40
    return mask
