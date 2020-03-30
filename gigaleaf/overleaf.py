from typing import Optional, Tuple, List
from dataclasses import dataclass
import os
import json
import getpass
from pathlib import Path

from gigaleaf.gigantum import Gigantum
from gigaleaf.utils import call_subprocess


@dataclass
class OverleafConfig:
    """Dataclass to store overleaf configuration data"""
    git_url: str
    local_git_dir: str
    integration_version: str


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
        """

        Returns:

        """
        output1 = self._git(['add', '-A'], self.overleaf_repo_directory)
        output2 = self._git(['commit', '-m', f'Updating linked Gigantum files ({Gigantum.get_current_revision()})'],
                            self.overleaf_repo_directory)

        return output1 + output2

    def pull(self) -> str:
        """

        Returns:

        """
        return self._git(['pull'], self.overleaf_repo_directory)

    def push(self) -> str:
        """

        Returns:

        """
        return self._git(['push'], self.overleaf_repo_directory)

    def _clone(self) -> None:
        """

        Returns:

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
                              integration_version=config_data['integration_version'])

    def _init_config(self) -> None:
        """Private method to configure an overleaf integration

        Returns:
            None
        """
        # Prompt for overleaf project URL
        intro_message = """
This Gigantum Project is not yet linked to an Overleaf project.
To do this, you must be able to use git based syncing, available with paid Overleaf plans. Note, this requirement is
only on the *owner* of the project. You can learn more about Git and Overleaf here:
https://www.overleaf.com/learn/how-to/How_do_I_push_a_new_project_to_Overleaf_via_git%3F.

To start, get the 'git link' for the desired Overleaf Project:

  1. Open the project on Overleaf
  2. Click on the Overleaf Menu button at the top left corner
  3. Under the 'Sync' section, click on 'Git'
  4. Copy the url that looks something like 'https://git.overleaf.com/abcdef0123456789abcdef01'
  
"""
        print(intro_message)
        project_url = input("Overleaf Git url: ")

        # Prompt for email
        email_message = """

Next, provide the email address and password that you use to log into your Overleaf account. 
This will be used to authenticate you when syncing with Overleaf.

We'll save these to an untracked file locally at `output/untracked/overleaf/credentials.json`. This file will not
get synced and collaborators will have to enter their own Overleaf email and password if they want to update the 
Overleaf Project. 

"""
        print(email_message)
        email = input("Overleaf email: ")

        # Prompt for password
        password = getpass.getpass("Overleaf password: ")

        # Write overleaf config file
        config = {"overleaf_git_url": project_url,
                  "integration_version": "0.1"}
        with open(self.overleaf_config_file, 'wt') as cf:
            json.dump(config, cf)

        # Write creds file
        self._set_creds(email, password)

    def _get_creds(self) -> Tuple[str, str]:
        """

        Returns:

        """
        if not os.path.isfile(self.overleaf_credential_file):
            self._init_creds()

        with open(self.overleaf_credential_file, 'rt') as cf:
            data = json.load(cf)

        return data['email'], data['password']

    def _init_creds(self) -> None:
        # Prompt for email
        creds_message = """

To interact with Overleaf, you must provide the email address and password that you use to log into your Overleaf account.
This will be used to authenticate you when syncing with Overleaf.

We'll save these to an untracked file locally at `output/untracked/overleaf/credentials.json`. This file will not
get synced and other collaborators will have to enter their own Overleaf email and password if they want to update the 
Overleaf Project, just as you are doing now. 

"""
        print(creds_message)
        email = input("Overleaf email: ")

        # Prompt for password
        password = getpass.getpass("Overleaf password: ")

        # Write creds file
        self._set_creds(email, password)

    def _set_creds(self, email: str, password: str) -> None:
        """

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
