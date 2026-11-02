"""Redis stream message rules. Bad schemas go to tf.dead and never become orders."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pydantic import ValidationError

from tf_models.bus import DECISION_ID_OPTIONAL, STALE_DROP_TYPES, BusMessage


def accept_message(raw: dict) -> tuple[BusMessage | None, str | None]:
    """Return (message, None) or (None, reason). Missing mode is a drop."""

    if "mode" not in raw or raw.get("mode") not in ("PAPER", "LIVE"):
        return None, "missing_mode"
    try:
        message = BusMessage.model_validate(raw)
    except ValidationError:
        return None, "bad_schema"
    if message.decision_id is None and message.type not in DECISION_ID_OPTIONAL:
        return None, "missing_decision_id"
    return message, None


def stale_entry(message: BusMessage, now: datetime, *, max_age_sec: int = 60) -> bool:
    """Entry signals older than max_age_sec are dropped. Fills and commands are not."""

    if message.type not in STALE_DROP_TYPES:
        return False
    if now.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware UTC")
    age = now.astimezone(timezone.utc) - message.ts_utc.astimezone(timezone.utc)
    return age > timedelta(seconds=max_age_sec)
