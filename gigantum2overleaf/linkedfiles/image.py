from typing import Optional

from gigantum2overleaf.linkedfiles.linkedfile import LinkedFile
from gigantum2overleaf.linkedfiles.metadata import ImageFileMetadata


class ImageFile(LinkedFile):

    def _load(self) -> ImageFileMetadata:
        """

        Returns:

        """
        data = self._load_metadata()
        return ImageFileMetadata(data['gigantum_relative_path'],
                                 data['gigantum_version'],
                                 data['classname'],
                                 data['content_hash'],
                                 data['label'],
                                 data['width'],
                                 data['alignment'],
                                 data['caption'])

    def write_snippet(self) -> None:
        """

        Returns:

        """
        if not isinstance(self.metadata, ImageFileMetadata):
            raise ValueError(f"Incorrect metadata type loaded: {type(self.metadata)}")

        with open(self.subfile_filename, 'wt') as sf:
            sf.write(self.metadata.label)
            sf.write(self.metadata.caption or "no caption")
            sf.write(self.metadata.classname)
