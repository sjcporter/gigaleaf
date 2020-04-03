from typing import Union, List
from pathlib import Path
import json
import glob

from gigaleaf.linkedfiles.image import ImageFile
from gigaleaf.linkedfiles.csv import CsvFile


def load_linked_file(metadata_filename: str) -> Union[ImageFile, CsvFile]:
    """Helper to load a LinkedFile child instance from an metadata file absolute path

    Args:
        metadata_filename: Absolute path to a metadata file

    Returns:
        LinkedFile child class instance
    """
    if not Path(metadata_filename).is_file():
        raise ValueError(f"Failed to load linked file: {metadata_filename}")

    with open(metadata_filename, 'rt') as mf:
        data = json.load(mf)

    if data['classname'] == 'ImageFile':
        return ImageFile(metadata_filename)
    elif data['classname'] == 'CsvFile':
        return CsvFile(metadata_filename)
    else:
        raise ValueError(f"Unsupported LinkedFile type: {data['classname']}")


def load_all_linked_files(overleaf_project_dir: str) -> List[Union[ImageFile, CsvFile]]:
    """Helper to load all LinkedFile child instances for a given Overleaf Project

    Args:
        overleaf_project_dir:

    Returns:

    """
    linked_files = list()
    for mf in glob.glob(Path(overleaf_project_dir, 'gigantum', 'metadata', '*.json').as_posix()):
        linked_files.append(load_linked_file(mf))

    return linked_files
