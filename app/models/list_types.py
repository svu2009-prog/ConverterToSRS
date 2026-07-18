from __future__ import annotations

from enum import Enum, auto


class ListType(Enum):
    DOMAINS = auto()
    IPV4 = auto()
    IPV6 = auto()
    MIXED = auto()


class RuleSetVersion(Enum):
    V1 = 1
    V2 = 2
    V3 = 3
    V4 = 4


class OutputFileType(Enum):
    LST = auto()
    JSON = auto()
    SRS = auto()
