from dataclasses import dataclass
from enum import Enum


class LinkType(Enum):
    TEXT = "Text"
    VIDEO = "Video"
    PICTURES = "Pictures"


@dataclass
class ScrappedLink:
    url: str
    linkType: LinkType
    data: str  # text content (max 1025 chars) or s3 location for non-text types
