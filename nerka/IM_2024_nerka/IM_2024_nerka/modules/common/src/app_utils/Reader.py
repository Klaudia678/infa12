import os
import pickle
import sys
from enum import Enum
from typing import Union, Optional, Any

import numpy as np

from modules.common.src.app_utils.Logger import get_logger, log_execution
from modules.common.src.model import DAG
from modules.common.src.model.VolumeData import VolumeData

FIGURE_DIR = '../results/figures/'


class OutputType(Enum):
    DAG_OUTPUT = "pkl"
    ARRAY_OUTPUT = "npz"


class Reader:
    DATA_DIR = './data/numpy/'

    class DataStep(Enum):

        DAG_FILENAME = ('dag', OutputType.DAG_OUTPUT)
        DAG_WITH_STATS_FILENAME = ('dag_with_stats', OutputType.DAG_OUTPUT)
        MORPHOLOGICAL_SKELETON = ('morphological_skeleton', OutputType.ARRAY_OUTPUT)
        TRIMMED_SKELETON = ('trimmed_skeleton', OutputType.ARRAY_OUTPUT)
        SKELETON_THICKNESS_FILENAME = ('central-line-radii', OutputType.ARRAY_OUTPUT)
        SKELETON_FILENAME = ('central-line', OutputType.ARRAY_OUTPUT)
        SKELETON_NEW = ('skeleton-new', OutputType.ARRAY_OUTPUT)
        RECONSTRUCTION_FILENAME = ('reconstruction', OutputType.ARRAY_OUTPUT)
        WHOLE_SKELETON_THICKNESS_FILENAME = ('WholeSkeletonThickness', OutputType.ARRAY_OUTPUT)
        REGISTERED_VOLUME = ('RegisteredVolume', OutputType.ARRAY_OUTPUT)
        REGISTERED_ZOOMED = ('RegisteredZoomed', OutputType.ARRAY_OUTPUT)
        ROOT_FILENAME = ('root', OutputType.ARRAY_OUTPUT)

        def get_name(self, size_str: str = '') -> str:
            return self.value[0] + size_str + "." + self.value[1].value

        def is_dag(self) -> bool:
            return self.value[1] == OutputType.DAG_OUTPUT

        def is_volume(self) -> bool:
            return self.value[1] == OutputType.ARRAY_OUTPUT

    class DirType(Enum):
        DIR_TYPE_GENERATED = 'G'
        DIR_TYPE_MODEL = 'M'
        DIR_TYPE_SPECIMEN = 'P'

    def __init__(self, tree_name: str, force_override: bool = False, use_cache: bool = True, default_size: int = None):
        self.__force_override = force_override
        self.tree_name = tree_name
        self.__cache = {}
        self.__use_cache = use_cache
        self.__size_string = "" if default_size in [0, None] else f'_{default_size}'

    @staticmethod
    def get_all_data_folders() -> list[str]:
        return os.listdir(Reader.DATA_DIR)

    @staticmethod
    def filter_data_folders_by_type(dir_type: DirType) -> list[str]:
        return [x for x in Reader.get_all_data_folders() if x[0] == dir_type.value]

    def get_size_str(self) -> str:
        return self.__size_string

    def set_force_override(self, p_force_override) -> None:
        self.__force_override = p_force_override

    def save_data(self, data: Union[VolumeData, DAG.DAG], filename: DataStep) -> None:
        if isinstance(data, DAG.DAG):
            self.__save_dag(data, filename)
        elif isinstance(data, VolumeData) or isinstance(data, np.ndarray):
            self.__save_step(data, filename)
        else:
            raise NotImplementedError

    @log_execution
    def load_data(self, filename: DataStep) -> Union[VolumeData, DAG.DAG]:
        data = self.__cache.get(filename, None)
        if data is None:
            if filename.is_dag():
                data = self.__load_dag(filename)
            elif filename.is_volume():
                data = self.__load_step(filename)
            if self.__use_cache:
                self.__cache[filename] = data
        if data is None:
            get_logger().warning(f'No data file found: {self.tree_name}/{filename.get_name()}')
        return data

    def dump(self, data: any, filename: str) -> None:
        pickle.dump(data, open(self.__get_full_dir(), 'wb'))

    def __get_full_dir(self):
        return self.DATA_DIR + self.tree_name + '/'

    def get_full_name(self, filename: DataStep) -> str:
        return self.__get_full_dir() + filename.get_name(self.__size_string)

    def __raise_exception_if_exist_and_should_not_be_overwritten(self, full_name):
        if os.path.exists(full_name) and (not self.__force_override):
            get_logger().error(
                f'File {full_name} already exists, use force_override=True if file should be overwritten')
            raise IOError(f'File {full_name} already exists')

    def __save_step(self, data: Union[VolumeData, np.ndarray], filename: DataStep) -> None:
        full_name = self.get_full_name(filename)
        self.__raise_exception_if_exist_and_should_not_be_overwritten(full_name)
        get_logger().debug(f'Saving {full_name}')
        np.savez_compressed(full_name, data=data)
        get_logger().debug(f'{full_name} saved successfully')

    def __load_step(self, name: DataStep) -> Optional[VolumeData]:
        exists, full_name = self.datafile_exists(name)
        if not exists:
            get_logger().error(f'Requested file {full_name} does not exist')
            return None
        get_logger().debug(f'Loading {full_name}')
        if full_name[-1] == 'z':
            data: VolumeData = np.load(full_name)['data']
        else:
            data: VolumeData = np.load(full_name)
        get_logger().debug(f'{full_name} loaded successfully')
        return data

    def __save_dag(self, dag: DAG.DAG, filename: DataStep):
        full_name = self.get_full_name(filename)
        get_logger().debug(f'Saving dag {full_name}')
        self.__raise_exception_if_exist_and_should_not_be_overwritten(full_name)
        dag.save(full_name)
        get_logger().debug(f'Dag {full_name} saved')

    def __load_dag(self, filename: DataStep) -> DAG.DAG:
        sys.path.append('./modules/common/src/')
        sys.modules['DAG'] = DAG
        with open(self.get_full_name(filename), 'rb') as input_:
            dag = pickle.load(input_)
            return dag

    def datafile_exists(self, filename: DataStep):
        full_name = self.get_full_name(filename)
        return os.path.exists(full_name), full_name

    def __repr__(self) -> str:
        return self.tree_name


def get_readers(dir_names: list[str], to_left: list = None, default_size: int = None, use_cache: bool = False,
                force_override: bool = False) -> list[Reader]:
    return [Reader(x, default_size=default_size, use_cache=use_cache, force_override=force_override) for x in dir_names
            if (to_left is None or x in to_left)]


def save_figure(plt: Any, type_name: str, tree_name: str) -> None:
    if not os.path.exists(FIGURE_DIR):
        os.mkdir(FIGURE_DIR)
    fig_dir = f'{FIGURE_DIR}{type_name}'
    if not os.path.exists(fig_dir):
        os.mkdir(fig_dir)
    plt.savefig(f'{FIGURE_DIR}{type_name}/{tree_name}.png')
