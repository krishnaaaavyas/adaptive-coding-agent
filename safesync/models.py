"""Small immutable values shared by planning and execution."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ActionType(str, Enum):
    COPY = "COPY"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SKIP = "SKIP"


@dataclass(frozen=True)
class SyncConfig:
    source: Path
    destination: Path
    delete_extra: bool = False
    ignore: tuple[str, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, "source", Path(self.source))
        object.__setattr__(self, "destination", Path(self.destination))
        if type(self.delete_extra) is not bool:
            raise ValueError("delete_extra must be a boolean")
        if isinstance(self.ignore, str):
            raise ValueError("ignore must be a sequence of glob patterns")
        patterns = tuple(self.ignore)
        if any(not isinstance(p, str) or not p or "\\" in p for p in patterns):
            raise ValueError("ignore patterns must be nonempty strings using '/' separators")
        object.__setattr__(self, "ignore", patterns)


@dataclass(frozen=True)
class FileEntry:
    path: str
    size: int
    sha256: str


@dataclass(frozen=True)
class SyncAction:
    kind: ActionType
    path: str
    source: FileEntry | None = None
    destination: FileEntry | None = None


@dataclass(frozen=True)
class SyncPlan:
    config: SyncConfig
    actions: tuple[SyncAction, ...]

    def __post_init__(self):
        object.__setattr__(self, "actions", tuple(self.actions))


@dataclass(frozen=True)
class ActionResult:
    action: SyncAction | None
    error: str | None = None


@dataclass(frozen=True)
class SyncReport:
    results: tuple[ActionResult, ...] = ()
    unattempted: int = 0

    def __post_init__(self):
        object.__setattr__(self, "results", tuple(self.results))

    def _count(self, kind):
        return sum(r.error is None and r.action is not None and r.action.kind == kind
                   for r in self.results)

    @property
    def copied(self):
        return self._count(ActionType.COPY)

    @property
    def updated(self):
        return self._count(ActionType.UPDATE)

    @property
    def deleted(self):
        return self._count(ActionType.DELETE)

    @property
    def skipped(self):
        return self._count(ActionType.SKIP)

    @property
    def failed(self):
        return sum(r.error is not None for r in self.results)

    def as_dict(self):
        return {
            "copied": self.copied, "updated": self.updated,
            "deleted": self.deleted, "skipped": self.skipped,
            "failed": self.failed, "unattempted": self.unattempted,
            "failures": [
                {"path": r.action.path if r.action else None, "error": r.error}
                for r in self.results if r.error is not None
            ],
        }
