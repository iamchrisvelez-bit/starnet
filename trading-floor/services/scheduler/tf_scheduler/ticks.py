from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from tf_models.bus import StreamName


def schedule_tick(mode: str, name: str, now: datetime | None = None) -> dict:
    ts = now or datetime.now(timezone.utc)
    return {
        "stream": StreamName.SCHEDULE,
        "message": {
            "event_id": str(uuid4()),
            "decision_id": None,
            "type": "schedule_tick",
            "producer": "scheduler",
            "schema_version": 1,
            "mode": mode,
            "ts_utc": ts.isoformat(),
            "payload": {"name": name},
        },
    }


def heartbeat(mode: str, now: datetime | None = None) -> dict:
    ts = now or datetime.now(timezone.utc)
    return {
        "stream": StreamName.HEARTBEAT,
        "message": {
            "event_id": str(uuid4()),
            "decision_id": None,
            "type": "heartbeat",
            "producer": "scheduler",
            "schema_version": 1,
            "mode": mode,
            "ts_utc": ts.isoformat(),
            "payload": {"service": "scheduler"},
        },
    }
