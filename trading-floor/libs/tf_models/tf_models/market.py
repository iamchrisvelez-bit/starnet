from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from tf_models.common import UtcDatetime


class Quote(BaseModel):
    model_config = ConfigDict(extra="forbid")

    venue: str
    symbol: str
    bid: Decimal | None
    ask: Decimal | None
    last: Decimal
    ts_utc: UtcDatetime
    received_at_utc: UtcDatetime
