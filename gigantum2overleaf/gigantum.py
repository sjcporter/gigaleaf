

class Gigantum:
    @staticmethod
    def get_gigantum_directory() -> str:
        """Method to get the project directory

        Returns:
            str
        """
        return "/mnt/labbook/.gigantum"

    @staticmethod
    def get_overleaf_repo_directory() -> str:
        """Method to get the project directory

        Returns:
            str
        """
        return "/mnt/labbook/.gigantum/output/untracked/overleaf"
