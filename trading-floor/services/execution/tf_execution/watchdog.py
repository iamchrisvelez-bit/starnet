"""Heartbeat fail-closed rules. Cancel ours only at the configured dead-man age."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

REQUIRED = ("data", "risk", "execution", "scheduler")


class BeatLevel(str, Enum):
    OK = "ok"
    HALT_ENTRIES = "halt_entries"
    HALT_ALL = "halt_all"
    CANCEL = "cancel"


def assess(
    beats: dict[str, datetime | None],
    now: datetime,
    *,
    started_at: datetime,
    block_sec: int,
    cancel_sec: int,
) -> BeatLevel:
    if now.tzinfo is None or started_at.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware UTC")
    stale_block: list[str] = []
    for name in REQUIRED:
        last = beats.get(name)
        if last is None:
            age = (now - started_at).total_seconds()
        else:
            if last.tzinfo is None:
                raise ValueError("timestamps must be timezone-aware UTC")
            age = (now - last).total_seconds()
        if age >= cancel_sec:
            return BeatLevel.CANCEL
        if age >= block_sec:
            stale_block.append(name)
    if not stale_block:
        return BeatLevel.OK
    if any(name in {"risk", "execution"} for name in stale_block):
        return BeatLevel.HALT_ALL
    return BeatLevel.HALT_ENTRIES
