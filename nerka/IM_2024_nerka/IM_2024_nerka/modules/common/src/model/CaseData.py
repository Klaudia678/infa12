from modules.common.src.app_utils.Reader import Reader
from modules.common.src.model.DAG import DAG
from modules.common.src.model.VolumeData import VolumeData


class CaseData:

    def __init__(self, reader: Reader, volume=None):
        self.__volume = volume
        self.__skeleton = None
        self.__thickness = None
        self.__dag = None
        self.__reader = reader

    def get_dag(self) -> DAG:
        if self.__dag is None:
            self.__dag = self.__reader.load_data(Reader.DataStep.DAG_WITH_STATS_FILENAME)
        return self.__dag

    def get_volume(self) -> VolumeData:
        if self.__volume is None:
            self.__volume = self.__reader.load_data(Reader.DataStep.RECONSTRUCTION_FILENAME)
        return self.__volume

    def get_skeleton(self) -> VolumeData:
        if self.__skeleton is None:
            self.__skeleton = self.__reader.load_data(Reader.DataStep.SKELETON_FILENAME)
        return self.__skeleton

    def get_thickness(self) -> VolumeData:
        if self.__thickness is None:
            self.__thickness = self.__reader.load_data(Reader.DataStep.SKELETON_THICKNESS_FILENAME)
        return self.__thickness
