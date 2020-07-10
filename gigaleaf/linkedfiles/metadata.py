from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class LinkedFileMetadata:
    gigantum_relative_path: str
    gigantum_version: str
    classname: str
    content_hash: str


@dataclass
class ImageFileMetadata(LinkedFileMetadata):
    label: str
    width: str
    alignment: str
    caption: Optional[str] = None


@dataclass
class CsvFileMetadata(LinkedFileMetadata):
    label: str
    caption: Optional[str] = None


@dataclass
class DataframeFileMetadata(LinkedFileMetadata):
    to_latex_kwargs: Dict[str, Any]

