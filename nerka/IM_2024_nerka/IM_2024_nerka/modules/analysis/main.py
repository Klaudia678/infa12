import sys
import os

# Ustawienie ścieżki do katalogu głównego projektu
project_root = r"C:\Users\KlaudiaDyl\Documents\GitHub\infa12\nerka\IM_2024_nerka\IM_2024_nerka"
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from modules.common.src.app_utils.Logger import get_logger
from modules.common.src.app_utils.Reader import Reader, get_readers


dirs = Reader.filter_data_folders_by_type(Reader.DirType.DIR_TYPE_SPECIMEN)
readers = get_readers(dirs, to_left=['P01', 'P02', 'P03'])
for reader in readers:
    dag = reader.load_data(Reader.DataStep.DAG_WITH_STATS_FILENAME)
    get_logger().debug(dag.get_shape())
