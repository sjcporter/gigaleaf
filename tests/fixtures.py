import pytest
import os
import uuid
import tempfile
import zipfile
import pathlib
import shutil
import json

from unittest.mock import patch

from gigantum2overleaf.utils import call_subprocess
from gigantum2overleaf.gigantum import Gigantum


@pytest.fixture
def gigantum_project_fixture():
    unit_test_working_dir = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex)
    os.makedirs(unit_test_working_dir)

    test_dir = pathlib.Path(__file__).parent.absolute()
    test_project_path = os.path.join(test_dir, 'resources', 'example_project.zip')
    secret_file_path = os.path.join(test_dir, 'resources', 'secrets.json')
    with zipfile.ZipFile(test_project_path, 'r') as zip_ref:
        zip_ref.extractall(unit_test_working_dir)

    # Set the working dir to INSIDE the project
    unit_test_working_dir = os.path.join(unit_test_working_dir, 'overleaf-test-project')

    with open(secret_file_path, 'rt') as sf:
        secrets = json.load(sf)

    # Configure overleaf config file and secrets
    config_file_path = os.path.join(unit_test_working_dir, '.gigantum', 'overleaf.json')
    config = {"overleaf_git_url": secrets['git_url'],
              "integration_version": "0.1"}
    with open(config_file_path, 'wt') as cf:
        json.dump(config, cf)

    # Write credential file
    creds = {"email": secrets['email'],
             "password": secrets['password']}
    overleaf_dir = os.path.join(unit_test_working_dir, 'output/untracked/overleaf')
    os.makedirs(overleaf_dir)
    with open(os.path.join(overleaf_dir, 'credentials.json'), 'wt') as cf:
        json.dump(creds, cf)

    # Yield and run test
    with patch.object(Gigantum, "get_project_root") as patched_gigantum:
        patched_gigantum.return_value = unit_test_working_dir
        yield unit_test_working_dir

    # Clean up overleaf if it was set up
    overleaf_project_dir = os.path.join(overleaf_dir, 'project')
    gigantum_overleaf_dir = os.path.join(overleaf_project_dir, 'gigantum')
    if os.path.isdir(gigantum_overleaf_dir):
        # Remove gigantum dir in the project IN overleaf
        shutil.rmtree(gigantum_overleaf_dir)
        git_status = call_subprocess(['git', 'status'], overleaf_project_dir, check=True)
        if "nothing to commit, working tree clean" not in git_status:
            call_subprocess(['git', 'add', '-A'], overleaf_project_dir, check=True)
            call_subprocess(['git', 'commit', '-m', 'Cleaning up integration test'],
                            overleaf_project_dir, check=True)

            call_subprocess(['git', 'push'],
                            overleaf_project_dir, check=True)

    # Clean up test project
    shutil.rmtree(unit_test_working_dir)
