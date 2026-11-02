from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from tf_models.common import UtcDatetime


class StreamName:
    BARS = "tf.market.bars"
    BOOKS = "tf.market.books"
    HEALTH = "tf.market.health"
    SIGNALS = "tf.signals"
    RESEARCH = "tf.research"
    DECISIONS = "tf.decisions"
    RISK = "tf.risk"
    APPROVALS = "tf.approvals"
    ORDERS = "tf.orders"
    FILLS = "tf.fills"
    GUARDS = "tf.guards"
    HEARTBEAT = "tf.heartbeat"
    COMMANDS = "tf.commands"
    SCHEDULE = "tf.schedule"
    MOONIT = "tf.moonit"
    DEAD = "tf.dead"


DECISION_ID_OPTIONAL = frozenset({"heartbeat", "schedule_tick"})
STALE_DROP_TYPES = frozenset({"signal"})


class BusMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: UUID
    decision_id: UUID | None = None
    type: str
    producer: str
    schema_version: int = Field(ge=1)
    mode: Literal["PAPER", "LIVE"]
    ts_utc: UtcDatetime
    payload: dict
