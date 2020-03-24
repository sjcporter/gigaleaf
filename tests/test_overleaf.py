import os

from gigantum2overleaf.overleaf import Overleaf
from tests.fixtures import gigantum_project_fixture


class TestOverleaf:
    def test_load_and_clone(self, gigantum_project_fixture):
        overleaf = Overleaf()

        assert os.path.isdir(overleaf.overleaf_repo_directory)
        assert os.path.isfile(os.path.join(overleaf.overleaf_repo_directory, 'main.tex'))
