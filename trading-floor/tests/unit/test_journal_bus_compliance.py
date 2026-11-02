from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tf_bus.memory import InMemoryBus
from tf_bus.protocol import stale_entry
from tf_compliance.rules import evaluate_compliance
from tf_config.load import REQUIRED_ISSUERS, load_floor
from tf_journal.chain import JournalStore, event_hash
from tf_models.bus import BusMessage
from tf_models.journal import JournalKind
from tf_models.orders import ProductFlags
from tests.support import entry_intent


def test_hash_chain_and_replay() -> None:
    store = JournalStore()
    decision = uuid4()
    now = datetime(2026, 11, 2, 18, 0, tzinfo=timezone.utc)
    first = store.append(
        kind=JournalKind.signal,
        actor="test",
        mode="PAPER",
        payload={"n": 1},
        ts_utc=now,
        decision_id=decision,
    )
    second = store.append(
        kind=JournalKind.order_submitted,
        actor="execution",
        mode="PAPER",
        payload={"n": 2},
        ts_utc=now + timedelta(seconds=1),
        decision_id=decision,
    )
    store.verify()
    assert second.prev_hash == first.hash
    assert [event.kind for event in store.replay(decision)] == [JournalKind.signal, JournalKind.order_submitted]
    tampered = second.model_copy(update={"payload": {"n": 9}})
    assert event_hash(tampered) != second.hash
    assert not hasattr(store, "delete")
    assert not hasattr(store, "update")


def test_bus_drops_bad_schema_and_stale_signals() -> None:
    bus = InMemoryBus()
    now = datetime(2026, 11, 2, 18, 0, tzinfo=timezone.utc)
    assert bus.publish("tf.signals", {"type": "signal", "mode": "PAPER"}) is None
    assert bus.dead[0]["reason"] in {"missing_mode", "bad_schema", "missing_decision_id"}
    decision = str(uuid4())
    message = {
        "event_id": str(uuid4()),
        "decision_id": decision,
        "type": "signal",
        "producer": "strategy_runtime",
        "schema_version": 1,
        "mode": "PAPER",
        "ts_utc": (now - timedelta(seconds=90)).isoformat(),
        "payload": {},
    }
    accepted = bus.publish("tf.signals", message)
    assert accepted is not None
    assert stale_entry(accepted, now) is True
    command = {
        "event_id": str(uuid4()),
        "decision_id": str(uuid4()),
        "type": "command",
        "producer": "console_api",
        "schema_version": 1,
        "mode": "PAPER",
        "ts_utc": (now - timedelta(seconds=90)).isoformat(),
        "payload": {"action": "kill"},
    }
    kept = bus.publish("tf.commands", command)
    assert kept is not None
    assert stale_entry(kept, now) is False
    pending = bus.read_new("tf.commands", "execution")
    bus.ack("tf.commands", "execution", str(pending[0].event_id))
    assert bus.read_new("tf.commands", "execution") == []


def test_restricted_seeds_and_spot_rules(floor) -> None:
    now = datetime(2026, 11, 2, 18, 0, tzinfo=timezone.utc)
    for name in REQUIRED_ISSUERS:
        intent = entry_intent(issuer_name=name, symbol="MC.PA")
        result = evaluate_compliance(intent, floor, now=now, mode="PAPER")
        assert result["passed"] is False
    plain = evaluate_compliance(entry_intent(), floor, now=now, mode="PAPER")
    assert plain["passed"] is True
    leveraged = entry_intent(flags=ProductFlags(leverage=Decimal("2")))
    assert evaluate_compliance(leveraged, floor, now=now, mode="PAPER")["passed"] is False
    short = entry_intent(side="sell", intent="entry", position_qty=Decimal("0"))
    assert evaluate_compliance(short, floor, now=now, mode="PAPER")["passed"] is False


@settings(max_examples=40)
@given(
    leverage=st.decimals(min_value=Decimal("0"), max_value=Decimal("5"), allow_nan=False, places=2).filter(
        lambda value: value != Decimal("1")
    )
)
def test_leverage_other_than_one_never_passes(leverage: Decimal) -> None:
    floor = load_floor()
    now = datetime(2026, 11, 2, 18, 0, tzinfo=timezone.utc)
    intent = entry_intent(flags=ProductFlags(leverage=leverage))
    assert evaluate_compliance(intent, floor, now=now, mode="PAPER")["passed"] is False


def test_postgres_journal_sql_revokes_mutation() -> None:
    from pathlib import Path

    sql = Path("infra/postgres/init.sql")
    if not sql.is_file():
        sql = Path(__file__).resolve().parents[2] / "infra" / "postgres" / "init.sql"
    text = sql.read_text(encoding="utf-8").upper()
    assert "REVOKE UPDATE, DELETE" in text


def test_shipped_blanks_stay_blank(floor) -> None:
    assert floor.risk["shared"]["ai_daily_spend_cap_usd"] is None
    assert floor.risk["moonit"]["wallet_balance_cap_usd"] is None
    assert floor.risk["moonit"]["max_slippage_bps"] is None
    assert floor.fees["venues"]["coinbase_advanced"]["taker_bps"] is None
    assert floor.slippage["defaults_bps"]["BTC-USD"] == 5
    assert floor.venues["equities_enabled"] is False
    names = [item["name"] for item in floor.restricted["issuers"]]
    assert names == [
        "LVMH Moët Hennessy Louis Vuitton",
        "Christian Dior SE",
    ]


def test_heartbeat_message_may_omit_decision_id() -> None:
    message = BusMessage.model_validate(
        {
            "event_id": str(uuid4()),
            "type": "heartbeat",
            "producer": "data",
            "schema_version": 1,
            "mode": "PAPER",
            "ts_utc": datetime.now(timezone.utc).isoformat(),
            "payload": {"service": "data"},
        }
    )
    assert message.decision_id is None
