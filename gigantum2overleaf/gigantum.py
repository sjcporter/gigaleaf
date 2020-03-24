import os


class Gigantum:
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

    def initialize_project(self) -> None:
        """

        Returns:

        """
        pass
