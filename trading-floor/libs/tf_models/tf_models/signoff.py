from __future__ import annotations

import json
from typing import Literal, Mapping
from uuid import UUID

from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from tf_models.common import UtcDatetime

CANONICAL_FIELDS = (
    "signoff_id",
    "decision_id",
    "intent_sha256",
    "risk_yaml_sha256",
    "mode",
    "venue",
    "symbol",
    "side",
    "qty",
    "limit_price",
    "intent",
    "expires_at",
)


def canonical_bytes(fields: Mapping[str, str | None]) -> bytes:
    missing = [key for key in CANONICAL_FIELDS if key not in fields]
    if missing:
        raise ValueError(f"sign-off payload missing {missing}")
    extra = [key for key in fields if key not in CANONICAL_FIELDS]
    if extra:
        raise ValueError(f"sign-off payload has extra fields {extra}")
    body = {key: fields[key] for key in CANONICAL_FIELDS}
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class RiskSignOff(BaseModel):
    model_config = ConfigDict(extra="forbid")

    signoff_id: UUID
    decision_id: UUID
    order_intent_id: UUID
    intent_sha256: str
    risk_yaml_sha256: str
    mode: Literal["PAPER", "LIVE"]
    venue: str
    symbol: str
    side: Literal["buy", "sell"]
    qty: Decimal
    limit_price: Decimal | None
    intent: Literal["entry", "exit", "stop", "reduce", "guard_derisk"]
    issued_at_utc: UtcDatetime
    expires_at_utc: UtcDatetime
    token: str


class ComplianceSignOff(BaseModel):
    model_config = ConfigDict(extra="forbid")

    signoff_id: UUID
    decision_id: UUID
    intent_sha256: str
    mode: Literal["PAPER", "LIVE"]
    issued_at_utc: UtcDatetime
    expires_at_utc: UtcDatetime
    token: str
