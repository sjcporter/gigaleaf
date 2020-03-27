from string import Template
from pathlib import Path

from gigaleaf.linkedfiles.linkedfile import LinkedFile
from gigaleaf.gigantum import Gigantum
from gigaleaf.linkedfiles.metadata import ImageFileMetadata


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

        subfile_template = Template("""\documentclass[../../main.tex]{subfiles}

% Subfile autogenerated by gigaleaf
% Gigantum revision: $gigantum_version
% Image content hash: $content_hash
\\begin{document}

\\begin{figure}[bh]
\\includegraphics[width=$width, $alignment]{$filename}
\\label{$label}
{$caption}
\\end{figure}

\\end{document}
""")

        if self.metadata.caption:
            caption = f"\\caption{{{self.metadata.caption}}}"
        else:
            caption = "\n"

        subfile_populated = subfile_template.substitute(filename=Path(self.metadata.gigantum_relative_path).stem,
                                                        gigantum_version=Gigantum.get_current_revision(),
                                                        content_hash=self.metadata.content_hash,
                                                        width=self.metadata.width,
                                                        alignment=self.metadata.alignment,
                                                        caption=caption,
                                                        label=self.metadata.label)

        with open(self.subfile_filename, 'wt') as sf:
            sf.write(subfile_populated)
