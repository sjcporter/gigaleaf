from typing import Optional
from pathlib import Path
import shutil

from gigaleaf.overleaf import Overleaf
from gigaleaf.gigantum import Gigantum

from gigaleaf.linkedfiles.image import ImageFile
from gigaleaf.linkedfiles.csv import CsvFile
from gigaleaf.linkedfiles import load_linked_file, load_all_linked_files


class Gigaleaf:
    """Class to link Gigantum Project outputs to an Overleaf Project"""
    def __init__(self) -> None:
        self.overleaf = Overleaf()
        self.gigantum = Gigantum(self.overleaf.overleaf_repo_directory)

    def link_image(self, gigantum_relative_path: str, caption: Optional[str] = None, label: Optional[str] = None,
                   width: str = "0.5\\textwidth", alignment: str = 'center') -> None:
        """Method to link an image file to your Overleaf project for automatic updating

        Args:
            gigantum_relative_path: relative path to the file, e.g. `output/my_fig.png`
            caption: The caption for the figure in the auto-generated latex subfile
            label: The label for the figure in the auto-generated latex subfile
            width: A string setting the width of the figure for the figure in the auto-generated latex subfile
            alignment: A string setting the alignment for the figure in the auto-generated latex subfile. Supported
                       values are `left, right, center, inner, and outer`


        If this method is called more than once for a given `gigantum_relative_path`, the link will simply be updated.
        This is useful for doing things like editing a caption.


        Returns:
            None
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
        """Method to unlink an image file from your Overleaf project.

        Args:
            relative_path: relative path to the file, e.g. `output/my_fig.png`

        Returns:
            None
        """
        metadata_filename = ImageFile.get_metadata_filename(relative_path)
        metadata_abs_filename = Path(Gigantum.get_overleaf_root_directory(),
                                     'project', 'gigantum', 'metadata', metadata_filename)
        img_file = load_linked_file(metadata_abs_filename.as_posix())
        img_file.unlink()

    def link_csv(self, gigantum_relative_path: str, caption: Optional[str] = None,
                 label: Optional[str] = None) -> None:
        """Method to link a csv file to your Overleaf project for automatic updating

        Args:
            gigantum_relative_path: relative path to the file, e.g. `output/my_table.csv`
            caption: The caption for the table in the auto-generated latex subfile
            label: The label for the table in the auto-generated latex subfile

        Returns:
            None
        """
        if not label:
            safe_filename = ImageFile.get_safe_filename(gigantum_relative_path)
            label = f"table:{Path(safe_filename).stem}"

        kwargs = {"caption": caption,
                  "label": label}

        CsvFile.link(gigantum_relative_path, **kwargs)

    def unlink_csv(self, relative_path: str) -> None:
        """Method to unlink a csv file from your Overleaf project.

        Args:
            relative_path: relative path to the file, e.g. `output/my_table.csv`

        Returns:
            None
        """
        metadata_filename = ImageFile.get_metadata_filename(relative_path)
        metadata_abs_filename = Path(Gigantum.get_overleaf_root_directory(),
                                     'project', 'gigantum', 'metadata', metadata_filename)
        csv_file = load_linked_file(metadata_abs_filename.as_posix())
        csv_file.unlink()

    def sync(self) -> None:
        """Method to synchronize your Gigantum and Overleaf projects.

        When you call this method, gigaleaf will do the following:

            * Pull changes from the Overleaf project
            * Check all linked files for changes. If changes exist it will update files in the Overleaf project
            * Commit changes to the Overleaf project
            * Push changes to the Overleaf project

        Returns:
            None
        """
        print("Syncing with Overleaf. Please wait...")
        self.overleaf.pull()

        linked_files = load_all_linked_files(self.overleaf.overleaf_repo_directory)
        for lf in linked_files:
            lf.update()

        self.overleaf.commit()

        self.overleaf.push()
        print("Sync complete.")

    def delete(self) -> None:
        """Removes the link between a Gigantum Project from an Overleaf Project

        Returns:
            None
        """
        self.overleaf.pull()

        # Remove Gigantum dir from Overleaf Project
        gigantum_overleaf_dir = Path(self.overleaf.overleaf_repo_directory, 'gigantum').as_posix()
        shutil.rmtree(gigantum_overleaf_dir)

        # Commit and Push
        self.overleaf.commit()
        self.overleaf.push()

        # Remove Overleaf Project dir and credentials from Gigantum Project
        shutil.rmtree(self.gigantum.get_overleaf_root_directory())

        # Remove gigaleaf config file from Gigantum Project, commit.
        Path(self.overleaf.overleaf_config_file).unlink()
        self.gigantum.commit_overleaf_config_file(self.overleaf.overleaf_config_file)

