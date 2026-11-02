from __future__ import annotations

from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductFlags(BaseModel):
    """Spot-only bits. Any true flag, or leverage other than 1, is a compliance reject."""

    model_config = ConfigDict(extra="forbid")

    margin: bool = False
    leverage: Decimal = Decimal("1")
    short: bool = False
    perpetual: bool = False
    option: bool = False
    lending: bool = False
    staking: bool = False
    withdraw: bool = False


class OrderIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision_id: UUID
    venue: str
    market: Literal["crypto", "equities", "solana_memecoin"]
    symbol: str
    side: Literal["buy", "sell"]
    order_type: Literal["limit", "market"]
    qty: Decimal
    limit_price: Decimal | None
    intent: Literal["entry", "exit", "stop", "reduce", "guard_derisk"]
    time_in_force: Literal["gtc", "ioc", "alo"] = "gtc"
    stop: Decimal | None = None
    issuer_name: str | None = None
    position_qty: Decimal = Decimal("0")
    flags: ProductFlags = Field(default_factory=ProductFlags)


class OrderStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    client_order_id: str
    venue_order_id: str
    decision_id: UUID
    symbol: str
    side: Literal["buy", "sell"]
    qty: Decimal
    limit_price: Decimal | None
    intent: Literal["entry", "exit", "stop", "reduce", "guard_derisk"]
    status: Literal["pending", "acked", "rejected", "partial", "filled", "cancelled"]
    ours: bool


class CancelReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cancelled: list[str]
    left_alone: list[str]
