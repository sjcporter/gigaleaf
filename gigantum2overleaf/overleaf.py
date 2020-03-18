from typing import Optional, Tuple
from dataclasses import dataclass
import os
import json

from gigantum2overleaf.gigantum import Gigantum


@dataclass
class OverleafConfig:
    """Dataclass to store overleaf configuration data"""
    project_git_url: str
    local_git_dir: str


class Overleaf:
    overleaf_config_file = os.path.join(Gigantum.get_gigantum_directory(), 'overleaf.json')

    def __init__(self) -> None:

        self.config: OverleafConfig = self._load_config()

        self._creds: Optional[Tuple[str, str]] = None

    def pull(self) -> None:
        pass

    def push(self) -> None:
        pass

    def _load_config(self) -> OverleafConfig:
        """Private method to load the overleaf configuration, including the username and password for syncing

        This will trigger an interactive configuration if needed.

        Returns:
            OverleafConfig
        """

        if not os.path.isfile(self.overleaf_config_file):
            self._init_config()

        with open(self.overleaf_config_file, 'rt') as of:
            config_data = json.load(of)

        return OverleafConfig(project_git_url=config_data['project_git_url'],
                              local_git_dir=Gigantum.get_overleaf_repo_directory())

    def _init_config(self) -> None:
        """Private method to configure an overleaf integration

        Returns:
            None
        """
        if not os.path.isfile(self.overleaf_config_file):
            raise ValueError("This project already appears to be configured with an overleaf project. Remove the "
                             "existing integration before adding a new one.")

        # Prompt for overleaf project URL

        # Prompt for email

        # Prompt for password

        # Write file

    def _get_creds(self) -> Tuple[str, str]:
        pass

    def _init_creds(self) -> None:
        pass

    def _set_creds(self) -> None:
        pass
