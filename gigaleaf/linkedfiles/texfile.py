from string import Template
from pathlib import Path

from gigaleaf.linkedfiles.linkedfile import LinkedFile
from gigaleaf.gigantum import Gigantum
from gigaleaf.linkedfiles.metadata import TexFileMetadata

try:
    import pandas  # type: ignore
except ImportError:
    pandas = None


class TexFile(LinkedFile):
    """A class for linking pickled pandas dataframe files"""

    def _should_copy_file(self) -> bool:
        """Method indicating True if when running `update()` the file is copied into Overleaf, or False if it should not

        Sometimes you need the file (e.g. an image) and sometimes you don't (e.g. a dataframe)

        Returns:
            bool
        """
        return True

    def _load(self) -> TexFileMetadata:
        """Method to load the metadata file into a dataclass

        Returns:
            TexFileMetadata
        """
        data = self._load_metadata()
        return TexFileMetadata(data['gigantum_relative_path'],
                                     data['gigantum_version'],
                                     data['classname'],
                                     data['content_hash'],
                                     data.get('additonal_args',{}))

    def write_subfile(self) -> None:
        """Method to write the Latex subfile

        Returns:
            None
        """
        if not isinstance(self.metadata, TexFileMetadata):
            raise ValueError(f"Incorrect metadata type loaded: {type(self.metadata)}")

        if pandas is None:
            raise EnvironmentError("Dataframe pickle file support requires pandas. "
                                   "Please run `pip install gigaleaf[pandas]`")

        subfile_template = Template(r"""\documentclass[../../main.tex]{subfiles}

% Subfile autogenerated by gigaleaf
% Gigantum revision: $gigantum_version
% Image content hash: $content_hash
\begin{document}

\input{$filename}

\end{document}
""")

        

        filename = "gigantum/data/" + Path(self.metadata.gigantum_relative_path).name

        subfile_populated = subfile_template.substitute(filename=filename,
                                                        gigantum_version=Gigantum.get_current_revision(),
                                                        content_hash=self.metadata.content_hash)

        Path(self.subfile_filename).write_text(subfile_populated)
