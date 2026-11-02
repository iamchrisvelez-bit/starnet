from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from tf_compliance.rules import evaluate_compliance, mint_compliance_signoff
from tf_config.load import FloorConfig
from tf_execution.paper import PaperEngine
from tf_execution.runtime import ExecutionRuntime
from tf_models.market import Quote
from tf_models.orders import OrderIntent
from tf_models.signoff import ComplianceSignOff, RiskSignOff
from tf_risk.check import evaluate_risk, mint_risk_signoff


def make_runtime(floor: FloorConfig, now: datetime, *, mode: str = "PAPER", live_confirmed: bool = False) -> ExecutionRuntime:
    runtime = ExecutionRuntime(
        mode=mode,
        live_confirmed=live_confirmed,
        paper=PaperEngine(maker_bps=None, taker_bps=None),
        risk_key=b"risk-test-key",
        compliance_key=b"compliance-test-key",
        risk_yaml_sha256=floor.risk_yaml_sha256,
        quote_max_age_sec=int(floor.risk["crypto"]["quote_max_age_sec"]),
        heartbeat_block_sec=int(floor.risk["shared"]["heartbeat_block_sec"]),
        heartbeat_cancel_sec=int(floor.risk["shared"]["heartbeat_cancel_sec"]),
    )
    runtime.boot(now)
    for service in ("data", "risk", "execution", "scheduler"):
        runtime.note_beat(service, now)
    return runtime


def fresh_quote(now: datetime, *, ask: str = "100", bid: str = "99", symbol: str = "BTC-USD") -> Quote:
    return Quote(
        venue="paper_engine",
        symbol=symbol,
        bid=Decimal(bid),
        ask=Decimal(ask),
        last=Decimal(bid),
        ts_utc=now,
        received_at_utc=now,
    )


def entry_intent(**overrides: object) -> OrderIntent:
    payload: dict[str, object] = {
        "decision_id": uuid4(),
        "venue": "paper_engine",
        "market": "crypto",
        "symbol": "BTC-USD",
        "side": "buy",
        "order_type": "limit",
        "qty": Decimal("0.1"),
        "limit_price": Decimal("90"),
        "intent": "entry",
        "stop": Decimal("80"),
    }
    payload.update(overrides)
    return OrderIntent(**payload)  # type: ignore[arg-type]


def sign_pair(intent: OrderIntent, floor: FloorConfig, now: datetime, *, mode: str = "PAPER") -> tuple[RiskSignOff, ComplianceSignOff]:
    risk = evaluate_risk(intent, floor, now=now, quote=fresh_quote(now))
    compliance = evaluate_compliance(intent, floor, now=now, mode=mode)
    if not risk["passed"] or not compliance["passed"]:
        raise AssertionError({"risk": risk, "compliance": compliance})
    risk_sign = mint_risk_signoff(
        intent,
        key=b"risk-test-key",
        mode=mode,
        now=now,
        risk_yaml_sha256=floor.risk_yaml_sha256,
    )
    compliance_sign = mint_compliance_signoff(
        intent,
        key=b"compliance-test-key",
        mode=mode,
        now=now,
        risk_yaml_sha256=floor.risk_yaml_sha256,
    )
    return risk_sign, compliance_sign
