from pathlib import Path
import json
import shutil

from gigaleaf import Gigaleaf
from gigaleaf.gigantum import Gigantum
from tests.fixtures import gigantum_project_fixture


class TestDataframeFile:
    def test_link_csv_file_and_sync(self, gigantum_project_fixture):
        gigaleaf = Gigaleaf()

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'table_pkl.json').is_file() is False

        gigaleaf.link_dataframe('../output/table.pkl', to_latex_kwargs={"index": False, "caption": "My table"})

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'table_pkl.json').is_file() is True

        gigaleaf.sync()

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'subfiles',
                    'table_pkl.tex').is_file() is True

        # Delete everything in untracked, reinit, and should still see the files
        shutil.rmtree(gigaleaf.overleaf.overleaf_repo_directory)
        gigaleaf = None

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'table_pkl.json').is_file() is False
        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'subfiles',
                    'table_pkl.tex').is_file() is False
        gigaleaf = Gigaleaf()
        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'table_pkl.json').is_file() is True
        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'subfiles',
                    'table_pkl.tex').is_file() is True

    def test_unlink_csv(self, gigantum_project_fixture):
        gigaleaf = Gigaleaf()

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'table_pkl.json').is_file() is False

        gigaleaf.link_dataframe('../output/table.pkl', to_latex_kwargs={"index": False, "caption": "My table"})

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'table_pkl.json').is_file() is True

        gigaleaf.sync()

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'subfiles',
                    'table_pkl.tex').is_file() is True

        gigaleaf.unlink_dataframe('../output/table.pkl')

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'table_pkl.json').is_file() is False
        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'subfiles',
                    'table_pkl.tex').is_file() is False

        gigaleaf.sync()

        # Delete everything in untracked, reinit, and should still not see the files
        shutil.rmtree(gigaleaf.overleaf.overleaf_repo_directory)
        gigaleaf = None

        gigaleaf = Gigaleaf()
        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'table_pkl.json').is_file() is False
        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'subfiles',
                    'table_pkl.tex').is_file() is False
