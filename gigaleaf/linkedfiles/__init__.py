from typing import Union, List
from pathlib import Path
import json
import glob

from gigaleaf.linkedfiles.image import ImageFile


def load_linked_file(metadata_filename: str) -> Union[ImageFile]:
    """

    Args:
        metadata_filename:

    Returns:

    """
    if not Path(metadata_filename).is_file():
        raise ValueError(f"Failed to load linked file: {metadata_filename}")

    with open(metadata_filename, 'rt') as mf:
        data = json.load(mf)

    if data['classname'] == 'ImageFile':
        return ImageFile(metadata_filename)
    else:
        raise ValueError(f"Unsupported LinkedFile type: {data['classname']}")


def load_all_linked_files(overleaf_project_dir: str) -> List[Union[ImageFile]]:
    """

    Args:
        overleaf_project_dir:

    Returns:

    """
    linked_files = list()
    for mf in glob.glob(Path(overleaf_project_dir, 'gigantum', 'metadata', '*.json').as_posix()):
        linked_files.append(load_linked_file(mf))

    return linked_files
