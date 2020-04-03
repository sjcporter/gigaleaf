from pathlib import Path
import json
import shutil

from gigaleaf import Gigaleaf
from gigaleaf.gigantum import Gigantum
from tests.fixtures import gigantum_project_fixture


class TestCsvFile:
    def test_link_csv_file_and_sync(self, gigantum_project_fixture):
        gigaleaf = Gigaleaf()

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'test_csv.json').is_file() is False

        gigaleaf.link_csv('output/test.csv', caption="My Cool Table", label="myfig1")

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'test_csv.json').is_file() is True

        gigaleaf.sync()

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'data',
                    'test.csv').is_file() is True

        # Delete everything in untracked, reinit, and should still see the files
        shutil.rmtree(gigaleaf.overleaf.overleaf_repo_directory)
        gigaleaf = None

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'test_csv.json').is_file() is False
        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'data',
                    'test.csv').is_file() is False
        gigaleaf = Gigaleaf()
        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'test_csv.json').is_file() is True
        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'data',
                    'test.csv').is_file() is True

    def test_update_csv(self, gigantum_project_fixture):
        gigaleaf = Gigaleaf()

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'test_csv.json').is_file() is False

        gigaleaf.link_csv('output/test.csv', caption="My Cool Table", label="myfig1")

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'test_csv.json').is_file() is True

        gigaleaf.sync()

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'data',
                    'test.csv').is_file() is True

        metadata_file = Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata', 'test_csv.json')
        with open(metadata_file, 'rt') as mf:
            data = json.load(mf)

        first_hash = data['content_hash']

        test_dir = Path(__file__).parent.absolute()
        shutil.copyfile(Path(test_dir, 'resources', 'test.csv').as_posix(),
                        Path(Gigantum.get_project_root(), 'output', 'test.csv'))

        gigaleaf.sync()

        with open(metadata_file, 'rt') as mf:
            data = json.load(mf)

        assert first_hash != data['content_hash']

    def test_unlink_csv(self, gigantum_project_fixture):
        gigaleaf = Gigaleaf()

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'test_csv.json').is_file() is False

        gigaleaf.link_csv('output/test.csv', caption="My Cool Table", label="myfig1")

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'test_csv.json').is_file() is True

        gigaleaf.sync()

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'data',
                    'test.csv').is_file() is True

        gigaleaf.unlink_image('output/test.csv')

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'test_csv.json').is_file() is False
        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'data',
                    'test.csv').is_file() is False

        gigaleaf.sync()

        # Delete everything in untracked, reinit, and should still not see the files
        shutil.rmtree(gigaleaf.overleaf.overleaf_repo_directory)
        gigaleaf = None

        gigaleaf = Gigaleaf()
        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'test_csv.json').is_file() is False
        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'data',
                    'test.csv').is_file() is False
