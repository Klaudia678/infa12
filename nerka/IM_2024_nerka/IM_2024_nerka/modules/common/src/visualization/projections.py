from abc import abstractmethod

import numpy as np
from matplotlib import pyplot as plt

from modules.common.src.app_utils.Logger import get_logger
from modules.common.src.model import Edge
from modules.common.src.model import DAG
from modules.common.src.model.VolumeData import VolumeData


class AbstractPixelGenerator:
    name: str = ''

    def get_volume(self):
        volume = np.zeros(self.get_shape())
        for voxel in self.get_voxels():
            volume[voxel] = self.get_color(voxel)
        return volume

    def set_name(self, name: str) -> None:
        self.name = name

    def get_name(self) -> str:
        return self.name

    @abstractmethod
    def get_voxels(self, projections=None) -> list[tuple]:
        pass

    @abstractmethod
    def get_shape(self) -> tuple:
        pass

    @abstractmethod
    def get_color(self, coords: tuple) -> int:
        pass

    @abstractmethod
    def get_colormap(self) -> str:
        pass


class DAGBasedPixelGenerator(AbstractPixelGenerator):

    def get_colormap(self) -> str:
        return 'gist_rainbow'

    def __init__(self, dag: DAG, color_function, color_limit=np.inf):
        self.dag: DAG = dag
        self.color_map = {}
        self.color_function = color_function
        self.color_limit = color_limit

    def get_color(self, voxel: tuple) -> int:
        return self.color_map[voxel]

    def get_shape(self) -> tuple:
        return tuple(map(lambda i, j: i + j, self.dag.get_shape(), (2, 2, 2)))

    def get_voxels(self, projections=None) -> list[tuple]:
        pixel_list = []
        for e in self.dag.edges:
            for voxel in e['voxels']:
                color = self.color_function(e)
                if color < self.color_limit:
                    pixel_list.append(voxel)
                    self.color_map[voxel] = color
        return pixel_list


class VolumeBasedPixelGenerator(AbstractPixelGenerator):

    def get_colormap(self) -> str:
        return 'binary'

    def __init__(self, volume: VolumeData):
        self.volume = volume

    def get_voxels(self, projections=None) -> np.ndarray:
        return np.argwhere(self.volume > 0)

    def get_shape(self) -> tuple:
        return self.volume.shape

    def get_color(self, coords: tuple) -> int:
        return 1


class SingleSlicePixelGenerator(AbstractPixelGenerator):

    def get_colormap(self) -> str:
        return 'Greys'

    def get_voxels(self, projections=None) -> list[tuple]:
        voxels = []
        if projections == 2:
            for i in range(self.volume.shape[0]):
                for j in range(self.volume.shape[1]):
                    voxels.append((i, j, self.slice_no))
        elif projections == 1:
            for i in range(self.volume.shape[0]):
                for j in range(self.volume.shape[1]):
                    voxels.append((i, self.slice_no, j))
        else:
            for i in range(self.volume.shape[1]):
                for j in range(self.volume.shape[2]):
                    voxels.append((self.slice_no, i, j))
        return voxels

    def get_shape(self) -> tuple:
        return self.volume.shape

    def get_color(self, coords: tuple) -> int:
        return self.volume[coords]

    def __init__(self, volume: VolumeData, slice_no: int):
        self.volume = volume
        self.slice_no = slice_no


class PixelProviderFactory:

    @staticmethod
    def get_pixel_factory(source: any) -> AbstractPixelGenerator:
        if isinstance(source, DAG.DAG):
            return DAGBasedPixelGenerator(source, Edge.get_generation, 9)
        if isinstance(source, VolumeData) or isinstance(source, np.ndarray):
            return VolumeBasedPixelGenerator(source)
        raise NotImplementedError()


def plot_as_2d_projection(pixel_generator: AbstractPixelGenerator, coords_to_highlight: np.ndarray = None, max_value=np.inf) -> any:
    fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(12, 4))
    plt.title(pixel_generator.get_name())
    for projection in (0, 1, 2):
        plt.sca(axs[projection])
        slice_shape = list(pixel_generator.get_shape())
        del slice_shape[projection]
        plot = np.zeros(slice_shape)
        voxels = pixel_generator.get_voxels(projection)
        for voxel in voxels:
            pixel = __get_2d_pixel(projection, voxel)
            try:
                plot[pixel] = max(plot[pixel], pixel_generator.get_color(voxel))
            except IndexError as e:
                get_logger().warning(f'Pixel: {pixel} is out of plot shape: {plot.shape}')
        __draw_highlighted_nodes(projection, coords_to_highlight, plot)
        points = np.argwhere((plot > 0))
        colors = []
        for p in points:
            c = plot[p[0], p[1]]
            if c <= max_value:
                colors.append(c)
            else:
                colors.append(0)
        colors[0] = 0  # Setting to zero to ensure colormap starting from zero
        plt.scatter(points[:, 0], points[:, 1], c=colors, s=(72. / fig.dpi) ** 2, lw=0, marker='^', cmap=pixel_generator.get_colormap())
    return plt


def __get_2d_pixel(axes: int, voxel: tuple) -> tuple:
    coords = []
    if axes == 0:
        coords = voxel[1:3]
    elif axes == 1:
        coords = (voxel[0], voxel[2])
    elif axes == 2:
        coords = voxel[0: 2]
    return tuple(coords)


def __draw_highlighted_nodes(axes: int, coords_to_highlight: np.ndarray, plot):
    if coords_to_highlight is not None:
        for coords in coords_to_highlight:
            __draw_root(plot, __get_2d_pixel(axes, voxel=coords))


def __draw_root(plot: np.ndarray, coords: tuple) -> None:
    for i in range(-10, 10):
        for j in range(-10, 10):
            try:
                plot[tuple(map(lambda x, y: x + y, coords, (i, j)))] = 2
            except IndexError:
                pass


def plot_2d_image(image: np.ndarray) -> None:
    plt.figure(figsize=(15, 10))
    plt.imshow(image.T)
    plt.show()
