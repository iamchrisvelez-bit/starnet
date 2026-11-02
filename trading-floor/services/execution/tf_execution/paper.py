"""Internal paper book. Fills rest until they cross. Fees come from config or the fill is refused."""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from tf_models.market import Quote
from tf_models.orders import CancelReport, OrderIntent, OrderStatus


class FeeScheduleMissing(RuntimeError):
    pass


class PaperEngine:
    venue = "paper_engine"
    market = "crypto"

    def __init__(self, *, maker_bps: Decimal | None, taker_bps: Decimal | None) -> None:
        self.maker_bps = maker_bps
        self.taker_bps = taker_bps
        self.open_orders: dict[str, OrderStatus] = {}
        self.foreign: dict[str, OrderStatus] = {}
        self.fills: list[dict] = []
        self._acks: dict[str, OrderStatus] = {}
        self._seq = 0

    def account_permissions(self) -> dict:
        return {
            "can_trade": True,
            "can_withdraw": False,
            "can_transfer": False,
            "eligibility_ok": True,
        }

    def health(self) -> dict:
        return {"venue": self.venue, "connected": True, "market": self.market}

    def seed_foreign(self, client_order_id: str, symbol: str = "BTC-USD") -> None:
        self.foreign[client_order_id] = OrderStatus(
            client_order_id=client_order_id,
            venue_order_id=f"foreign-{client_order_id}",
            decision_id=uuid4(),
            symbol=symbol,
            side="buy",
            qty=Decimal("1"),
            limit_price=Decimal("1"),
            intent="entry",
            status="acked",
            ours=False,
        )

    def submit(self, intent: OrderIntent, client_order_id: str, quote: Quote | None) -> OrderStatus:
        existing = self._acks.get(client_order_id)
        if existing is not None:
            return existing
        self._seq += 1
        status = OrderStatus(
            client_order_id=client_order_id,
            venue_order_id=f"paper-{self._seq}",
            decision_id=intent.decision_id,
            symbol=intent.symbol,
            side=intent.side,
            qty=intent.qty,
            limit_price=intent.limit_price,
            intent=intent.intent,
            status="acked",
            ours=client_order_id.startswith("tf_"),
        )
        crossed = _crosses(intent, quote)
        if crossed:
            fee = self._fee(intent.qty, _fill_price(intent, quote))
            status = status.model_copy(update={"status": "filled"})
            self.fills.append(
                {
                    "client_order_id": client_order_id,
                    "decision_id": intent.decision_id,
                    "price": _fill_price(intent, quote),
                    "fee": fee,
                    "liquidity": "taker",
                }
            )
        else:
            self.open_orders[client_order_id] = status
        self._acks[client_order_id] = status
        return status

    def cancel_all_ours(self) -> CancelReport:
        cancelled = []
        for client_order_id, order in list(self.open_orders.items()):
            if client_order_id.startswith("tf_"):
                self.open_orders[client_order_id] = order.model_copy(update={"status": "cancelled"})
                cancelled.append(client_order_id)
                del self.open_orders[client_order_id]
                self._acks[client_order_id] = self._acks[client_order_id].model_copy(update={"status": "cancelled"})
        left = list(self.foreign)
        return CancelReport(cancelled=cancelled, left_alone=left)

    def _fee(self, qty: Decimal, price: Decimal) -> Decimal:
        if self.taker_bps is None:
            raise FeeScheduleMissing("Refusing fill: fee schedule is unset")
        return (qty * price * self.taker_bps) / Decimal("10000")


def _fill_price(intent: OrderIntent, quote: Quote | None) -> Decimal:
    if quote is None:
        if intent.limit_price is None:
            raise FeeScheduleMissing("Refusing fill: no quote")
        return intent.limit_price
    if intent.side == "buy":
        return quote.ask if quote.ask is not None else quote.last
    return quote.bid if quote.bid is not None else quote.last


def _crosses(intent: OrderIntent, quote: Quote | None) -> bool:
    if intent.order_type == "market":
        return quote is not None
    if quote is None or intent.limit_price is None:
        return False
    if intent.side == "buy" and quote.ask is not None:
        return intent.limit_price >= quote.ask
    if intent.side == "sell" and quote.bid is not None:
        return intent.limit_price <= quote.bid
    return False
