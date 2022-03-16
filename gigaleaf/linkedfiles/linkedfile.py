from typing import Dict, Any, Union
from abc import ABC, abstractmethod
from pathlib import Path
import json
import hashlib
import shutil

from gigaleaf.gigantum import Gigantum
from gigaleaf.linkedfiles.metadata import ImageFileMetadata, LinkedFileMetadata


class LinkedFile(ABC):
    """Abstract class for Linked Files"""
    def __init__(self, metadata_file: str) -> None:
        self.metadata_filename = metadata_file
        self.metadata = self._load()

    def _load_metadata(self) -> Dict[str, Any]:
        """Method to load the metadata file from disk for the Linked File represented by this class

        Returns:
            metadata file contents as a dictionary
        """
        if not Path(self.metadata_filename).is_file():
            raise ValueError(f"Failed to load metadata file: {self.metadata_filename}")

        with open(self.metadata_filename, 'rt') as mf:
            data: Dict[str, Any] = json.load(mf)

        return data

    @abstractmethod
    def _load(self) -> Union[ImageFileMetadata, LinkedFileMetadata]:
        """Method to load the metadata for this Linked File and return a metadata dataclass instance

        Returns:

        """
        raise NotImplementedError

    @property
    def data_filename(self) -> str:
        """The absolute path to the linked file's data in the data directory

        The data directory is the location managed by gigaleaf where linked file contents are stored

        Returns:
            absolute path to the file
        """
        overleaf_gigantum_path = Path(Gigantum.get_overleaf_root_directory(),  'gigantum', 'data')
        return Path(overleaf_gigantum_path, Path(self.metadata.gigantum_relative_path).name).absolute().as_posix()

    @property
    def subfile_filename(self) -> str:
        """The absolute path to the Linked File's subfile in the subfiles directory

        The subfiles directory is the location managed by gigaleaf where all generated subfiles are stored

        Returns:
            absolute path to the subfile
        """
        filename = Path(self.metadata_filename).name
        filename = filename.replace('.json', '.tex')
        overleaf_gigantum_path = Path(Gigantum.get_overleaf_root_directory(), 'gigantum', 'subfiles')
        return Path(overleaf_gigantum_path, filename).absolute().as_posix()

    @staticmethod
    def get_safe_filename(relative_path: str) -> str:
        """Helper method to create a safe file name from the user's filename

        Args:
            relative_path: a filename

        Returns:
            a sanitized filename
        """
        stem = Path(relative_path).stem
        suffixes = Path(relative_path).suffixes
        for ch in ['`', '*', '_', '{', '}', '[', ']', '(', ')', '>',  '<', '#', '+', '.', '!', '$', ' ', '@', '&']:
            if ch in stem:
                stem = stem.replace(ch, '-')

        return stem + "".join(suffixes)

    @staticmethod
    def get_metadata_filename(gigantum_relative_path: str) -> str:
        """Returns the filename (not path) to the metadata file for a given file

        Args:
            gigantum_relative_path: The relative path to a file in a Gigantum Project

        Returns:
            metadata filename
        """
        # Create metadata file name, but sanitizing, moving the suffix into the filename, and adding .json
        filename = Path(gigantum_relative_path).stem
        suffixes = Path(gigantum_relative_path).suffixes

        safe_filename = LinkedFile.get_safe_filename(filename)

        # move file suffix into the file name
        suffix_str = ""
        for suffix in suffixes:
            suffix_str = suffix_str + suffix.replace('.', '_')

        return safe_filename + suffix_str + ".json"

    @classmethod
    def link(cls, relative_path: str, **kwargs: Dict[str, Any]) -> None:
        """Method to link a file output in a Gigantum Project to an Overleaf project

        Args:
            relative_path: relative path to the file from the current working dir, e.g. `../output/my_fig.png`
            **kwargs: args specific to each LinkedFile implementation

        Returns:
            None
        """
        file_path = Path(relative_path).resolve()
        if file_path.is_file() is False:
            # File provided does not exist
            raise ValueError(f"The file {file_path} does not exist. Provide a relative path from the working"
                             f"directory to your file. In Jupyter, the working directory is the directory containing "
                             f"your notebook.")

        metadata_filename = cls.get_metadata_filename(relative_path)
        metadata_abs_filename = Path(Gigantum.get_overleaf_root_directory(),
                                     'gigantum', 'metadata', metadata_filename)

        if metadata_abs_filename.exists() is True:
            # This is an update to the link, so get the current content hash for the file.
            with open(metadata_abs_filename, 'rt') as mf:
                current_metadata: Dict[str, Any] = json.load(mf)
                content_hash = current_metadata['content_hash']
        else:
            # Set content hash to init so it is always detected as "modified" on first link
            content_hash = "init"

        full_kwargs = {
            "gigantum_relative_path": file_path.relative_to(Path(Gigantum.get_project_root()).resolve()).as_posix(),
            "gigantum_version": Gigantum.get_current_revision(),
            "classname": cls.__name__,
            "content_hash": content_hash,
            "metadata_filename": metadata_filename}
        full_kwargs.update(kwargs)

        cls.write_metadata(**full_kwargs)

    def _hash_file(self, filename: str) -> str:
        """Method to hash files for comparing contents and detecting updates

        Args:
            filename: absolute path to the file to hash

        Returns:
            md5 hash value
        """
        # Process files in 64kb chunks
        buffer_size = 65536  

        md5 = hashlib.md5()

        # Hash the file contents and metadata file together in case either change
        file_list = [filename, self.metadata_filename]

        for f in file_list:
            with open(f, 'rb') as fh:
                while True:
                    data = fh.read(buffer_size)
                    if not data:
                        break
                    md5.update(data)

        return md5.hexdigest()

    def _is_modified(self) -> bool:
        """Helper method to check if a file has been modified since the last time you ran .sync()

        Returns:
            true if the file has changed since the last time you ran .sync(), false if it has not
        """
        if self.metadata.content_hash != self._hash_file(Path(Gigantum.get_project_root(),
                                                         self.metadata.gigantum_relative_path).absolute().as_posix()):
            return True
        else:
            return False

    @abstractmethod
    def _should_copy_file(self) -> bool:
        """Method indicating True if when running `update()` the file is copied into Overleaf, or False if it should not

        Sometimes you need the file (e.g. an image) and sometimes you don't (e.g. a dataframe)

        Returns:
            bool
        """
        raise NotImplementedError

    def update(self) -> None:
        """Method to update the file contents, latex subfile, and metadata file.

        Returns:

        """
        if self._is_modified():
            if self._should_copy_file() is True:
                # Copy file if needed
                shutil.copyfile(Path(Gigantum.get_project_root(), self.metadata.gigantum_relative_path),
                                self.data_filename)

            # Update commit hash in metadata
            kwargs = {"content_hash": self._hash_file(Path(Gigantum.get_project_root(),
                                                           self.metadata.gigantum_relative_path).absolute().as_posix()),
                      "metadata_filename": self.metadata_filename}
            self.write_metadata(**kwargs)

            # Latex subfile
            self.write_subfile()

    def unlink(self) -> None:
        """Method to unlink a file by removing its contents, subfile, and metadata from the overleaf project

        Returns:

        """
        Path(self.metadata_filename).unlink()
        Path(self.subfile_filename).unlink()
        if self._should_copy_file() is True:
            # If you inserted data in the Overleaf project, remove it.
            Path(self.data_filename).unlink()

    @staticmethod
    def write_metadata(metadata_filename: str, **kwargs: Any) -> None:
        """Method to write metadata to disk

        Args:
            metadata_filename: name of the metadata file
            **kwargs:

        Returns:
            None
        """
        data = dict()
        if Path(metadata_filename).exists():
            # Update existing file
            with open(metadata_filename, 'rt') as mf:
                data = json.load(mf)

        data.update(kwargs)

        metadata_abs_filename = Path(Gigantum.get_overleaf_root_directory(),
                                     'gigantum', 'metadata', metadata_filename)
        with open(metadata_abs_filename, 'wt') as mf:
            json.dump(data, mf)

    @abstractmethod
    def write_subfile(self) -> None:
        """Abstract method to write the latex subfile specific to the child class

        Returns:
            None
        """
        raise NotImplemented
