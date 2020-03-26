from pathlib import Path
import json
import shutil

from gigantum2overleaf import G2O
from gigantum2overleaf.gigantum import Gigantum
from tests.fixtures import gigantum_project_fixture


class TestG2O:
    def test_empty_sync(self, gigantum_project_fixture):
        g2o = G2O()

        # should be a no-op and not error
        g2o.sync()

    def test_link_image_with_defaults(self, gigantum_project_fixture):
        g2o = G2O()

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'fig1_png.json').is_file() is False

        g2o.link_image('output/fig1.png')

        metadata_file = Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata', 'fig1_png.json')
        assert metadata_file.is_file() is True

        with open(metadata_file, 'rt') as mf:
            data = json.load(mf)

        assert data['gigantum_relative_path'] == 'output/fig1.png'
        assert data['gigantum_version'] == '8e88dedc2aacca66e60d93a1fedd2eddb24851be'
        assert data['classname'] == 'ImageFile'
        assert data['content_hash'] == 'init'
        assert data['caption'] is None
        assert data['label'] == 'fig:fig1'
        assert data['width'] == '0.5\\textwidth'
        assert data['alignment'] == 'center'

    def test_link_image_and_sync(self, gigantum_project_fixture):
        g2o = G2O()

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'fig1_png.json').is_file() is False

        g2o.link_image('output/fig1.png')

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'fig1_png.json').is_file() is True

        g2o.sync()

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'data',
                    'fig1.png').is_file() is True

        # Delete everything in untracked, reinit, and should still see the files
        g2o = None
        shutil.rmtree(Gigantum.get_overleaf_root_directory())

        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'fig1_png.json').is_file() is False
        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'data',
                    'fig1.png').is_file() is False
        g2o = G2O()
        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'metadata',
                    'fig1_png.json').is_file() is True
        assert Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'data',
                    'fig1.png').is_file() is True

    def test_update_image(self, gigantum_project_fixture):
        pass

    def test_unlink_image(self, gigantum_project_fixture):
        pass
