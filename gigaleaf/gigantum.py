import os
from pathlib import Path

from gigaleaf.utils import call_subprocess


class Gigantum:
    def __init__(self, overleaf_project_root: str):
        self.setup_gigantum_in_overleaf(overleaf_project_root)

    @staticmethod
    def get_project_root() -> str:
        """Method to get the project root directory

        Returns:
            str
        """
        return "/mnt/labbook"

    @staticmethod
    def get_gigantum_directory() -> str:
        """Method to get the .gigantum directory

        Returns:
            str
        """
        return os.path.join(Gigantum.get_project_root(), ".gigantum")

    @staticmethod
    def get_overleaf_root_directory() -> str:
        """Method to get the root overleaf directory

        Returns:
            str
        """
        return os.path.join(Gigantum.get_project_root(), "output/untracked/overleaf")

    @staticmethod
    def get_current_revision() -> str:
        """Method to get the current git revision of the Gigantum Project repository

        Returns:
            str
        """
        return call_subprocess(['git', 'rev-parse', 'HEAD'], Gigantum.get_project_root()).strip()

    @staticmethod
    def setup_gigantum_in_overleaf(overleaf_project_root: str) -> None:
        """Method to populate the gigantum directory structure and readme in the Overleaf Project

        Returns:
            None
        """
        directories = [Path(overleaf_project_root, 'gigantum'),
                       Path(overleaf_project_root, 'gigantum', 'metadata'),
                       Path(overleaf_project_root, 'gigantum', 'data'),
                       Path(overleaf_project_root, 'gigantum', 'subfiles'),
                       ]

        for d in directories:
            if not d.is_dir():
                d.mkdir()

        if not Path(overleaf_project_root, 'gigantum', 'README.txt').is_file():
            readme = Path(Path(__file__).parent.absolute(), 'resources', 'gigantum_readme.txt').read_text()
            Path(overleaf_project_root, 'gigantum', 'README.txt').write_text(readme)

    @staticmethod
    def commit_overleaf_config_file(config_file_path: str) -> None:
        """Method to commit the Overleaf config file to the Gigantum Project repository

        Args:
            config_file_path:

        Returns:

        """
        call_subprocess(['git', 'add', config_file_path], Gigantum.get_project_root())
        call_subprocess(['git', 'commit', '-m', 'Adding Overleaf project config file.'], Gigantum.get_project_root())
