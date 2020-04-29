import pytest
from pathlib import Path
import json
import shutil

from gigaleaf import Gigaleaf
from gigaleaf.gigantum import Gigantum
from tests.fixtures import gigantum_project_fixture


class TestGigaleaf:
    def test_empty_sync(self, gigantum_project_fixture):
        gigaleaf = Gigaleaf()

        # should be a no-op and not error
        gigaleaf.sync()

    def test_link_image_does_not_exist(self, gigantum_project_fixture):
        gigaleaf = Gigaleaf()

        with pytest.raises(ValueError):
            gigaleaf.link_image('output/FILEDOESNOTEXIST.png')

    def test_link_image_with_defaults(self, gigantum_project_fixture):
        gigaleaf = Gigaleaf()

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'fig1_png.json').is_file() is False

        gigaleaf.link_image('output/fig1.png')

        metadata_file = Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata', 'fig1_png.json')
        assert metadata_file.is_file() is True

        with open(metadata_file, 'rt') as mf:
            data = json.load(mf)

        assert data['gigantum_relative_path'] == 'output/fig1.png'
        assert data['gigantum_version'] != 'init'
        assert len(data['gigantum_version']) == 40
        assert data['classname'] == 'ImageFile'
        assert data['content_hash'] == 'init'
        assert data['caption'] is None
        assert data['label'] == 'fig:fig1'
        assert data['width'] == '0.5\\textwidth'
        assert data['alignment'] == 'center'

    def test_link_image_and_sync(self, gigantum_project_fixture):
        gigaleaf = Gigaleaf()

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'fig1_png.json').is_file() is False

        gigaleaf.link_image('output/fig1.png', caption="My figure", label='fig111', alignment='right',
                            width='0.3\\textwidth')

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'fig1_png.json').is_file() is True

        gigaleaf.sync()

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'data',
                    'fig1.png').is_file() is True

        # Delete everything in untracked, reinit, and should still see the files
        shutil.rmtree(gigaleaf.overleaf.overleaf_repo_directory)
        gigaleaf = None

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'fig1_png.json').is_file() is False
        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'data',
                    'fig1.png').is_file() is False
        gigaleaf = Gigaleaf()
        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'fig1_png.json').is_file() is True
        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'data',
                    'fig1.png').is_file() is True

    def test_update_image(self, gigantum_project_fixture):

        gigaleaf = Gigaleaf()

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'fig1_png.json').is_file() is False

        gigaleaf.link_image('output/fig1.png', width='0.8\\textwidth')

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'fig1_png.json').is_file() is True

        gigaleaf.sync()

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'data',
                    'fig1.png').is_file() is True

        metadata_file = Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata', 'fig1_png.json')
        with open(metadata_file, 'rt') as mf:
            data = json.load(mf)

        first_hash = data['content_hash']

        test_dir = Path(__file__).parent.absolute()
        shutil.copyfile(Path(test_dir, 'resources', 'fig1.png').as_posix(),
                        Path(Gigantum.get_project_root(), 'output', 'fig1.png'))

        gigaleaf.sync()

        metadata_file = Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata', 'fig1_png.json')
        with open(metadata_file, 'rt') as mf:
            data = json.load(mf)

        assert first_hash != data['content_hash']

    def test_unlink_image(self, gigantum_project_fixture):
        gigaleaf = Gigaleaf()

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'fig1_png.json').is_file() is False

        gigaleaf.link_image('output/fig1.png')

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'fig1_png.json').is_file() is True

        gigaleaf.sync()

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'data',
                    'fig1.png').is_file() is True

        gigaleaf.unlink_image('output/fig1.png')

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'fig1_png.json').is_file() is False
        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'data',
                    'fig1.png').is_file() is False

        gigaleaf.sync()

        # Delete everything in untracked, reinit, and should still not see the files
        shutil.rmtree(gigaleaf.overleaf.overleaf_repo_directory)
        gigaleaf = None

        gigaleaf = Gigaleaf()
        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'fig1_png.json').is_file() is False
        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'data',
                    'fig1.png').is_file() is False

    def test_delete_project_link(self, gigantum_project_fixture):
        gigaleaf = Gigaleaf()

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'fig1_png.json').is_file() is False

        gigaleaf.link_image('output/fig1.png')

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'fig1_png.json').is_file() is True

        gigaleaf.sync()

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'data',
                    'fig1.png').is_file() is True

        gigaleaf.delete()

        assert Path(Gigantum.get_overleaf_root_directory()).is_dir() is False
        assert Path(gigaleaf.overleaf.overleaf_config_file).is_file() is False

    def test_delete_project_when_empty(self, gigantum_project_fixture):
        gigaleaf = Gigaleaf()

        assert Path(gigaleaf.overleaf.overleaf_config_file).is_file() is True

        gigaleaf.delete()

        assert Path(Gigantum.get_overleaf_root_directory()).is_dir() is False
        assert Path(gigaleaf.overleaf.overleaf_config_file).is_file() is False
