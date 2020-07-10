from string import Template
from pathlib import Path

from gigaleaf.linkedfiles.linkedfile import LinkedFile
from gigaleaf.gigantum import Gigantum
from gigaleaf.linkedfiles.metadata import DataframeFileMetadata

try:
    import pandas  # type: ignore
except ImportError:
    pandas = None


class DataframeFile(LinkedFile):
    """A class for linking pickled pandas dataframe files"""

    def _should_copy_file(self) -> bool:
        """Method indicating True if when running `update()` the file is copied into Overleaf, or False if it should not

        Sometimes you need the file (e.g. an image) and sometimes you don't (e.g. a dataframe)

        Returns:
            bool
        """
        return False

    def _load(self) -> DataframeFileMetadata:
        """Method to load the metadata file into a dataclass

        Returns:
            DataframeFileMetadata
        """
        data = self._load_metadata()
        return DataframeFileMetadata(data['gigantum_relative_path'],
                                     data['gigantum_version'],
                                     data['classname'],
                                     data['content_hash'],
                                     data['to_latex_kwargs'])

    def write_subfile(self) -> None:
        """Method to write the Latex subfile

        Returns:
            None
        """
        if not isinstance(self.metadata, DataframeFileMetadata):
            raise ValueError(f"Incorrect metadata type loaded: {type(self.metadata)}")

        if pandas is None:
            raise EnvironmentError("Dataframe pickle file support requires pandas. "
                                   "Please run `pip install gigaleaf[pandas]`")

        subfile_template = Template(r"""\documentclass[../../main.tex]{subfiles}

% Subfile autogenerated by gigaleaf
% Gigantum revision: $gigantum_version
% Image content hash: $content_hash
\begin{document}

{$table}

\end{document}
""")

        with open(Path(Gigantum.get_project_root(),
                       self.metadata.gigantum_relative_path).absolute().as_posix(), 'rb') as f:
            df = pandas.read_pickle(f)
            table = df.to_latex(**self.metadata.to_latex_kwargs)

        filename = "gigantum/data/" + Path(self.metadata.gigantum_relative_path).name

        subfile_populated = subfile_template.substitute(filename=filename,
                                                        gigantum_version=Gigantum.get_current_revision(),
                                                        content_hash=self.metadata.content_hash,
                                                        table=table)

        Path(self.subfile_filename).write_text(subfile_populated)
