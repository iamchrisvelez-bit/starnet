"""Append-only journal hash chain. There is no update and no delete."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Iterable
from uuid import UUID, uuid4

from tf_models.common import format_ts
from tf_models.journal import JournalEvent, JournalKind

GENESIS_HASH = "0" * 64


def _jsonable(value: object) -> object:
    if isinstance(value, Decimal):
        rendered = format(value, "f")
        if "." in rendered:
            rendered = rendered.rstrip("0").rstrip(".")
        return rendered or "0"
    if isinstance(value, datetime):
        return format_ts(value)
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, JournalKind):
        return value.value
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def event_hash(event: JournalEvent) -> str:
    body = {
        "journal_id": str(event.journal_id),
        "decision_id": None if event.decision_id is None else str(event.decision_id),
        "parent_decision_id": None if event.parent_decision_id is None else str(event.parent_decision_id),
        "ts_utc": format_ts(event.ts_utc),
        "mode": event.mode,
        "kind": event.kind.value,
        "actor": event.actor,
        "schema_version": event.schema_version,
        "payload": _jsonable(event.payload),
        "prev_hash": event.prev_hash,
    }
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class JournalStore:
    """In-process append-only store. Postgres grants live in infra/postgres/init.sql."""

    def __init__(self) -> None:
        self._events: list[JournalEvent] = []

    def append(
        self,
        *,
        kind: JournalKind,
        actor: str,
        mode: str,
        payload: dict,
        ts_utc: datetime,
        decision_id: UUID | None = None,
        parent_decision_id: UUID | None = None,
        journal_id: UUID | None = None,
    ) -> JournalEvent:
        if ts_utc.tzinfo is None:
            raise ValueError("timestamps must be timezone-aware UTC")
        prev = self._events[-1].hash if self._events else GENESIS_HASH
        event = JournalEvent(
            journal_id=journal_id or uuid4(),
            decision_id=decision_id,
            parent_decision_id=parent_decision_id,
            ts_utc=ts_utc.astimezone(timezone.utc),
            mode=mode,  # type: ignore[arg-type]
            kind=kind,
            actor=actor,
            schema_version=1,
            payload=payload,
            prev_hash=prev,
            hash=GENESIS_HASH,
        )
        digest = event_hash(event)
        event = event.model_copy(update={"hash": digest})
        if event_hash(event) != event.hash:
            raise RuntimeError("journal hash failed to close")
        self._events.append(event)
        return event

    def verify(self) -> None:
        prev = GENESIS_HASH
        for event in self._events:
            if event.prev_hash != prev:
                raise ValueError("journal prev_hash break")
            if event_hash(event) != event.hash:
                raise ValueError("journal hash mismatch")
            prev = event.hash

    def replay(self, decision_id: UUID) -> list[JournalEvent]:
        matched = [event for event in self._events if event.decision_id == decision_id]
        return sorted(matched, key=lambda event: (event.ts_utc, str(event.journal_id)))

    def __iter__(self) -> Iterable[JournalEvent]:
        return iter(tuple(self._events))

    def __len__(self) -> int:
        return len(self._events)
