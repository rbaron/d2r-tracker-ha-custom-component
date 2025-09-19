from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, NewType, Optional


@dataclass
class TerrorZoneResponse:
    current: str
    next: Optional[str]
    updated_at: datetime


Progress = NewType("Progress", int)


@dataclass
class DCloneCoreProgress:
    HC: Progress
    SC: Progress


@dataclass
class DCloneLadderProgress:
    L: DCloneCoreProgress
    NL: DCloneCoreProgress


@dataclass
class DCloneProgress:
    Americas: DCloneLadderProgress
    Europe: DCloneLadderProgress
    Asia: DCloneLadderProgress
    # Newer release, may not be present.
    China: Optional[DCloneLadderProgress]


class ProviderBase:
    NAME: ClassVar[str]

    def get_terror_zone(self) -> TerrorZoneResponse:
        raise NotImplementedError

    def get_dclone_progress(self) -> DCloneProgress:
        raise NotImplementedError

    def get_attribution(self) -> str:
        raise NotImplementedError


@dataclass
class ProviderResponse:
    terror_zone: Optional[TerrorZoneResponse]
    dclone_progress: Optional[DCloneProgress]


REGIONS = list(DCloneProgress.__dataclass_fields__.keys())

LADDER = list(DCloneLadderProgress.__dataclass_fields__.keys())

HC = list(DCloneCoreProgress.__dataclass_fields__.keys())
