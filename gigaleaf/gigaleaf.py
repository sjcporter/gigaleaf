from typing import Optional, Dict, Any
from pathlib import Path
import shutil

from gigaleaf.overleaf import Overleaf
from gigaleaf.gigantum import Gigantum

from gigaleaf.linkedfiles.image import ImageFile
from gigaleaf.linkedfiles.csv import CsvFile
from gigaleaf.linkedfiles.dataframe import DataframeFile
from gigaleaf.linkedfiles import load_linked_file, load_all_linked_files


class Gigaleaf:
    """Class to link Gigantum Project outputs to an Overleaf Project"""
    def __init__(self) -> None:
        self.overleaf = Overleaf()
        self.gigantum = Gigantum(self.overleaf.overleaf_repo_directory)

    def link_image(self, relative_path: str, caption: Optional[str] = None, label: Optional[str] = None,
                   width: str = "0.5\\textwidth", alignment: str = 'center') -> None:
        """Method to link an image file to your Overleaf project for automatic updating

        Args:
            relative_path: relative path to the file from the current working dir, e.g. `../output/my_fig.png`
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
            safe_filename = ImageFile.get_safe_filename(relative_path)
            label = f"fig:{Path(safe_filename).stem}"

        kwargs: Dict[str, Any] = {"caption": caption,
                                  "label": label,
                                  "width": width,
                                  "alignment": alignment}

        ImageFile.link(relative_path, **kwargs)

    def unlink_image(self, relative_path: str) -> None:
        """Method to unlink an image file from your Overleaf project.

        Args:
            relative_path: relative path to the file from the current working dir, e.g. `../output/my_fig.png`

        Returns:
            None
        """
        metadata_filename = ImageFile.get_metadata_filename(relative_path)
        metadata_abs_filename = Path(Gigantum.get_overleaf_root_directory(),
                                     'project', 'gigantum', 'metadata', metadata_filename)
        img_file = load_linked_file(metadata_abs_filename.as_posix())
        img_file.unlink()

    def link_csv(self, relative_path: str, caption: Optional[str] = None,
                 label: Optional[str] = None) -> None:
        """Method to link a csv file to your Overleaf project for automatic updating

        Args:
            relative_path: relative path to the file from the current working dir, e.g. `../output/my_table.csv`
            caption: The caption for the table in the auto-generated latex subfile
            label: The label for the table in the auto-generated latex subfile

        Returns:
            None
        """
        if not label:
            safe_filename = ImageFile.get_safe_filename(relative_path)
            label = f"table:{Path(safe_filename).stem}"

        kwargs: Dict[str, Any] = {"caption": caption,
                                  "label": label}

        CsvFile.link(relative_path, **kwargs)

    def unlink_csv(self, relative_path: str) -> None:
        """Method to unlink a csv file from your Overleaf project.

        Args:
            relative_path: relative path to the file from the current working dir, e.g. `../output/my_table.csv`

        Returns:
            None
        """
        metadata_filename = ImageFile.get_metadata_filename(relative_path)
        metadata_abs_filename = Path(Gigantum.get_overleaf_root_directory(),
                                     'project', 'gigantum', 'metadata', metadata_filename)
        csv_file = load_linked_file(metadata_abs_filename.as_posix())
        csv_file.unlink()

    def link_dataframe(self, relative_path: str, to_latex_kwargs: Dict[str, Any]) -> None:
        """Method to link a dataframe file to your Overleaf project for automatic updating

        Args:
            relative_path: relative path to the file from the current working dir, e.g. `../output/my_table.csv`
            to_latex_kwargs: a dictionary of key word arguments to pass into the pandas.DataFrame.to_latex method
                             (https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_latex.html)

        Returns:
            None
        """
        # Clean kwargs sent to .to_latex()
        if 'buf' in to_latex_kwargs:
            del to_latex_kwargs['buf']

        kwargs = {"to_latex_kwargs": to_latex_kwargs}

        DataframeFile.link(relative_path, **kwargs)

    def unlink_dataframe(self, relative_path: str) -> None:
        """Method to unlink a dataframe file from your Overleaf project.

        Args:
            relative_path: relative path to the file from the current working dir, e.g. `../output/my_table.csv`

        Returns:
            None
        """
        metadata_filename = ImageFile.get_metadata_filename(relative_path)
        metadata_abs_filename = Path(Gigantum.get_overleaf_root_directory(),
                                     'project', 'gigantum', 'metadata', metadata_filename)
        dataframe_file = load_linked_file(metadata_abs_filename.as_posix())
        dataframe_file.unlink()

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
        gigaleaf_config_file = Path(self.overleaf.overleaf_config_file)
        if gigaleaf_config_file.is_file():
            print("Removing integration from Overleaf and Gigantum projects. Please wait...")
            self.overleaf.pull()

            gigantum_overleaf_dir = Path(self.overleaf.overleaf_repo_directory, 'gigantum')
            if gigantum_overleaf_dir.is_dir():
                # Remove Gigantum dir from Overleaf Project if it exists (maybe you haven't synced yet)
                shutil.rmtree(gigantum_overleaf_dir.as_posix())

                # Commit and Push
                try:
                    self.overleaf.commit()
                    self.overleaf.push()
                except ValueError as err:
                    if "Your branch is up to date with 'origin/master'" not in str(err):
                        # If you haven't synced yet, you'll get a git error because removing the dir doesn't actually
                        # change the repository state. If you get any other error, raise.
                        raise

            # Remove Overleaf Project dir and credentials from Gigantum Project
            overleaf_root_dir = Path(self.gigantum.get_overleaf_root_directory())
            if overleaf_root_dir.is_dir():
                shutil.rmtree(overleaf_root_dir.as_posix())

            # Remove gigaleaf config file from Gigantum Project & commit.
            gigaleaf_config_file.unlink()
            self.gigantum.commit_overleaf_config_file(gigaleaf_config_file.as_posix())
            print("Removal complete.")
        else:
            print("gigaleaf has not been configured yet. Skipping removal process.")

