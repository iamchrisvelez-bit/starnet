"""Quiet hours use America/New_York. Entries stop; stops, exits, and guard de-risks do not."""

from __future__ import annotations

from datetime import datetime, time
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
ENTRY_BLOCKED = frozenset({"entry"})
PROTECTIVE = frozenset({"exit", "stop", "reduce", "guard_derisk"})


def _minutes(value: str) -> int:
    hour, minute = value.split(":")
    parsed = time(int(hour), int(minute))
    return parsed.hour * 60 + parsed.minute


def in_quiet_hours(ts_utc: datetime, start_et: str = "23:00", end_et: str = "07:00") -> bool:
    if ts_utc.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware UTC")
    local = ts_utc.astimezone(ET)
    now_minutes = local.hour * 60 + local.minute
    start = _minutes(start_et)
    end = _minutes(end_et)
    if start == end:
        return False
    if start < end:
        return start <= now_minutes < end
    return now_minutes >= start or now_minutes < end


def quiet_hours_block_intent(intent: str, ts_utc: datetime, start_et: str, end_et: str) -> bool:
    if intent not in ENTRY_BLOCKED:
        return False
    return in_quiet_hours(ts_utc, start_et, end_et)
