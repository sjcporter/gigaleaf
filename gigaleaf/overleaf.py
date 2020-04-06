from typing import Optional, Tuple, List
from dataclasses import dataclass
import os
import json
import getpass
from pathlib import Path

from gigaleaf.gigantum import Gigantum
from gigaleaf.utils import call_subprocess
from gigaleaf import __version__ as gigaleaf_version


@dataclass
class OverleafConfig:
    """Dataclass to store overleaf configuration data"""
    git_url: str
    local_git_dir: str
    gigaleaf_version: str


class Overleaf:
    def __init__(self) -> None:
        """Load configuration or initialize on instance creation"""
        self.overleaf_config_file = os.path.join(Gigantum.get_gigantum_directory(), 'overleaf.json')
        self.overleaf_repo_directory = os.path.join(Gigantum.get_overleaf_root_directory(), 'project')
        self.overleaf_credential_file = os.path.join(Gigantum.get_overleaf_root_directory(), 'credentials.json')

        self.config: OverleafConfig = self._load_config()

        # Clone the Overleaf git repo if needed
        if os.path.isfile(self.overleaf_config_file):
            if not os.path.isdir(self.overleaf_repo_directory):
                # Overleaf project does not exist locally yet, clone
                self._clone()

    def _git(self, cmd_tokens: List[str], cwd: str) -> str:
        """Execute a subprocess call and properly benchmark and log

        Args:
            cmd_tokens: List of command tokens, e.g., ['ls', '-la']
            cwd: Current working directory

        Returns:
            Decoded stdout of called process after completing

        Raises:
            subprocess.CalledProcessError
        """
        email, password = self._get_creds()
        env_vars = os.environ
        env_vars['OVERLEAF_EMAIL'] = email
        env_vars['OVERLEAF_PASSWORD'] = password
        env_vars['GIT_ASKPASS'] = "gigaleaf_askpass"

        return call_subprocess(['git'] + cmd_tokens, cwd, check=True, shell=False, env=dict(env_vars))

    def commit(self) -> str:
        """Method to commit changes to the Overleaf git repository

        Returns:
            the output from git commands
        """
        output1 = self._git(['add', '-A'], self.overleaf_repo_directory)
        output2 = self._git(['commit', '-m', f'Updating linked Gigantum files ({Gigantum.get_current_revision()})'],
                            self.overleaf_repo_directory)

        return output1 + output2

    def pull(self) -> str:
        """Method to pull changes to the Overleaf git repository

        Returns:
            the output from the git command
        """
        return self._git(['pull'], self.overleaf_repo_directory)

    def push(self) -> str:
        """Method to pull changes to the Overleaf git repository

        Returns:
            the output from the git command
        """
        return self._git(['push'], self.overleaf_repo_directory)

    def _clone(self) -> None:
        """Method to clone the Overleaf project into the untracked section of the Gigantum Project

        Returns:
            the output from the git command
        """
        if os.path.isdir(self.overleaf_repo_directory):
            raise IOError("Repository already has been cloned.")

        os.makedirs(self.overleaf_repo_directory)

        print("Cloning Overleaf Project to output/untracked/overleaf/project")
        output = self._git(['clone', self.config.git_url, self.overleaf_repo_directory], self.overleaf_repo_directory)

        print(output)

    def _load_config(self) -> OverleafConfig:
        """Private method to load the overleaf configuration, including the username and password for syncing

        This will trigger an interactive configuration if needed.

        Returns:
            OverleafConfig
        """

        if not os.path.isfile(self.overleaf_config_file):
            # First time run, Prompt user and create configuration file
            self._init_config()

        with open(self.overleaf_config_file, 'rt') as of:
            config_data = json.load(of)

        return OverleafConfig(git_url=config_data['overleaf_git_url'],
                              local_git_dir=self.overleaf_repo_directory,
                              gigaleaf_version=config_data['gigaleaf_version'])

    def _init_config(self) -> None:
        """Private method to configure an overleaf integration

        Returns:
            None
        """
        # Prompt for overleaf project URL
        intro_message = Path(Path(__file__).parent.absolute(), 'resources', 'intro_message.txt').read_text()
        print(intro_message)

        project_url = input("Overleaf Git url: ")

        # Prompt for email and password
        self._init_creds()

        # Write overleaf config file
        config = {"overleaf_git_url": project_url,
                  "gigaleaf_version": gigaleaf_version}
        with open(self.overleaf_config_file, 'wt') as cf:
            json.dump(config, cf)

        # Commit the config file
        Gigantum.commit_overleaf_config_file(self.overleaf_config_file)

    def _get_creds(self) -> Tuple[str, str]:
        """Load the credential file. If missing, prompt the user.

        Returns:
            a tuple containing the email address and password
        """
        if not os.path.isfile(self.overleaf_credential_file):
            self._init_creds()

        with open(self.overleaf_credential_file, 'rt') as cf:
            data = json.load(cf)

        return data['email'], data['password']

    def _init_creds(self) -> None:
        """Method to prompt the user for credentials and save to an untracked file locally.

        Returns:
            None
        """
        # Prompt for email
        creds_message = Path(Path(__file__).parent.absolute(), 'resources', 'creds_message.txt').read_text()

        print(creds_message)
        email = getpass.getpass("Overleaf email: ")

        # Prompt for password
        password = getpass.getpass("Overleaf password: ")

        # Write creds file
        self._set_creds(email, password)

    def _set_creds(self, email: str, password: str) -> None:
        """ Write credentials to an untracked file

        Args:
            email: the Overleaf email to save
            password: the Overleaf password to save

        Returns:
            None
        """
        if not os.path.isdir(Gigantum.get_overleaf_root_directory()):
            os.makedirs(Gigantum.get_overleaf_root_directory())

        creds = {"email": email,
                 "password": password}

        with open(self.overleaf_credential_file, 'wt') as cf:
            json.dump(creds, cf)
