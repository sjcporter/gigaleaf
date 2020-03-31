from typing import Optional
from pathlib import Path

from gigaleaf.overleaf import Overleaf
from gigaleaf.gigantum import Gigantum

from gigaleaf.linkedfiles.image import ImageFile
from gigaleaf.linkedfiles.csv import CsvFile
from gigaleaf.linkedfiles import load_linked_file, load_all_linked_files


class Gigaleaf:
    def __init__(self) -> None:
        self.overleaf = Overleaf()
        self.gigantum = Gigantum(self.overleaf.overleaf_repo_directory)

    def link_image(self, gigantum_relative_path: str, caption: Optional[str] = None, label: Optional[str] = None,
                   width: str = "0.5\\textwidth", alignment: str = 'center') -> None:
        """

        Args:
            gigantum_relative_path:
            caption:
            label:
            width:
            alignment:

        Returns:

        """
        if not label:
            safe_filename = ImageFile.get_safe_filename(gigantum_relative_path)
            label = f"fig:{Path(safe_filename).stem}"

        kwargs = {"caption": caption,
                  "label": label,
                  "width": width,
                  "alignment": alignment}

        ImageFile.link(gigantum_relative_path, **kwargs)

    def unlink_image(self, relative_path: str) -> None:
        """

        Args:
            relative_path:

        Returns:

        """
        metadata_filename = ImageFile.get_metadata_filename(relative_path)
        metadata_abs_filename = Path(Gigantum.get_overleaf_root_directory(),
                                     'project', 'gigantum', 'metadata', metadata_filename)
        img_file = load_linked_file(metadata_abs_filename.as_posix())
        img_file.unlink()

    def link_csv(self, gigantum_relative_path: str, caption: Optional[str] = None,
                 label: Optional[str] = None) -> None:
        """

        Args:
            gigantum_relative_path:
            caption:
            label:

        Returns:

        """
        if not label:
            safe_filename = ImageFile.get_safe_filename(gigantum_relative_path)
            label = f"table:{Path(safe_filename).stem}"

        kwargs = {"caption": caption,
                  "label": label}

        CsvFile.link(gigantum_relative_path, **kwargs)

    def unlink_csv(self, relative_path: str) -> None:
        """

        Args:
            relative_path:

        Returns:

        """
        metadata_filename = ImageFile.get_metadata_filename(relative_path)
        metadata_abs_filename = Path(Gigantum.get_overleaf_root_directory(),
                                     'project', 'gigantum', 'metadata', metadata_filename)
        csv_file = load_linked_file(metadata_abs_filename.as_posix())
        csv_file.unlink()

    def sync(self) -> None:
        """

        Returns:

        """
        self.overleaf.pull()

        linked_files = load_all_linked_files(self.overleaf.overleaf_repo_directory)
        for lf in linked_files:
            lf.update()

        self.overleaf.commit()

        self.overleaf.push()

    def unlink_project(self) -> None:
        """

        Returns:

        """
        raise NotImplemented
