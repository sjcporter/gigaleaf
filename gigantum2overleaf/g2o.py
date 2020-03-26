from typing import Optional
from pathlib import Path

from gigantum2overleaf.overleaf import Overleaf
from gigantum2overleaf.gigantum import Gigantum

from gigantum2overleaf.linkedfiles.image import ImageFile
from gigantum2overleaf.linkedfiles import load_linked_file, load_all_linked_files


class G2O:
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

        kwargs = {"gigantum_relative_path": gigantum_relative_path,
                  "caption": caption,
                  "label": label,
                  "width": width,
                  "alignment": alignment}

        ImageFile.link(**kwargs)

    def unlink_image(self, relative_path: str) -> None:
        """

        Args:
            relative_path:

        Returns:

        """
        metadata_filename = ImageFile.get_metadata_filename(relative_path)
        img_file = load_linked_file(metadata_filename)
        img_file.unlink()

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
        pass
