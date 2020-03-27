from typing import Optional, Dict, Any, Union
from abc import ABC, abstractmethod
from pathlib import Path
import json
import hashlib
import shutil

from gigaleaf.gigantum import Gigantum
from gigaleaf.linkedfiles.metadata import ImageFileMetadata, LinkedFileMetadata


class LinkedFile(ABC):
    def __init__(self, metadata_file: str) -> None:
        self.metadata_filename = metadata_file
        self.metadata = self._load()

    def _load_metadata(self) -> Dict[str, Any]:
        """

        Returns:

        """
        if not Path(self.metadata_filename).is_file():
            raise ValueError(f"Failed to load metadata file: {self.metadata_filename}")

        with open(self.metadata_filename, 'rt') as mf:
            data: Dict[str, Any] = json.load(mf)

        return data

    @abstractmethod
    def _load(self) -> Union[ImageFileMetadata, LinkedFileMetadata]:
        """

        Returns:

        """
        raise NotImplemented

    @property
    def data_filename(self) -> str:
        """

        Returns:

        """
        overleaf_gigantum_path = Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'data')
        return Path(overleaf_gigantum_path, Path(self.metadata.gigantum_relative_path).name).absolute().as_posix()

    @property
    def subfile_filename(self) -> str:
        """

        Returns:

        """
        filename = Path(self.metadata_filename).name
        filename = filename.replace('.json', '.tex')
        overleaf_gigantum_path = Path(Gigantum.get_overleaf_root_directory(), 'project', 'gigantum', 'subfiles')
        return Path(overleaf_gigantum_path, filename).absolute().as_posix()

    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """

        Args:
            filename:

        Returns:

        """
        stem = Path(filename).stem
        suffixes = Path(filename).suffixes
        for ch in ['`', '*', '_', '{', '}', '[', ']', '(', ')', '>',  '<', '#', '+', '.', '!', '$', ' ', '@', '&']:
            if ch in stem:
                stem = stem.replace(ch, '-')

        return stem + "".join(suffixes)

    @staticmethod
    def get_metadata_filename(gigantum_relative_path: str) -> str:
        """

        Args:
            gigantum_relative_path:

        Returns:

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
    def link(cls, gigantum_relative_path: str, **kwargs: Any) -> None:
        """

        Args:
            gigantum_relative_path:
            **kwargs:

        Returns:

        """
        metadata_filename = cls.get_metadata_filename(gigantum_relative_path)

        full_kwargs = {"gigantum_relative_path": gigantum_relative_path,
                       "gigantum_version": Gigantum.get_current_revision(),
                       "classname": cls.__name__,
                       "content_hash": "init",  # Set content hash to init so it is detected as "modified"
                       "metadata_filename": metadata_filename}
        full_kwargs.update(kwargs)

        cls.write_metadata(**full_kwargs)

    @staticmethod
    def _hash_file(filename: str) -> str:
        """

        Args:
            filename:

        Returns:

        """
        BUFFER_SIZE = 65536  # Process in 64kb chunks

        md5 = hashlib.md5()

        with open(filename, 'rb') as fh:
            while True:
                data = fh.read(BUFFER_SIZE)
                if not data:
                    break
                md5.update(data)

        return md5.hexdigest()

    def _is_modified(self) -> bool:
        """

        Returns:

        """
        if self.metadata.content_hash != self._hash_file(Path(Gigantum.get_project_root(),
                                                         self.metadata.gigantum_relative_path).absolute().as_posix()):
            return True
        else:
            return False

    def update(self) -> None:
        """

        Returns:

        """
        if self._is_modified():
            # Copy file
            shutil.copyfile(Path(Gigantum.get_project_root(), self.metadata.gigantum_relative_path),
                            self.data_filename)

            # Update commit hash in metadata
            kwargs = {"content_hash": self._hash_file(Path(Gigantum.get_project_root(),
                                                           self.metadata.gigantum_relative_path).absolute().as_posix()),
                      "metadata_filename": self.metadata_filename}
            self.write_metadata(**kwargs)

            # Snippet
            self.write_snippet()

    def unlink(self) -> None:
        """

        Returns:

        """
        Path(self.metadata_filename).unlink()
        Path(self.data_filename).unlink()
        Path(self.subfile_filename).unlink()

    @staticmethod
    def write_metadata(metadata_filename: str, **kwargs: Any) -> None:
        """

        Args:
            metadata_filename:
            **kwargs:

        Returns:

        """
        data = dict()
        if Path(metadata_filename).exists():
            # Update existing file
            with open(metadata_filename, 'rt') as mf:
                data = json.load(mf)

        data.update(kwargs)

        metadata_abs_filename = Path(Gigantum.get_overleaf_root_directory(),
                                     'project', 'gigantum', 'metadata', metadata_filename)
        with open(metadata_abs_filename, 'wt') as mf:
            json.dump(data, mf)

    @abstractmethod
    def write_snippet(self) -> None:
        pass
