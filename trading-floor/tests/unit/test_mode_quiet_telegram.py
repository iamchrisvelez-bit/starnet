from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from tf_execution.mode import confirm_live, resolve_mode
from tf_models.signoff import canonical_bytes
from tf_risk.check import discard_quiet_entries, evaluate_risk
from tf_risk.quiet import in_quiet_hours
from tf_comms.telegram import deliver, format_outbound
from tests.support import entry_intent, fresh_quote

ET = ZoneInfo("America/New_York")


def test_mode_defaults_and_live_phrase() -> None:
    assert resolve_mode(None) == "PAPER"
    assert resolve_mode("") == "PAPER"
    assert resolve_mode("paper") == "PAPER"
    assert resolve_mode("live") == "LIVE"
    with pytest.raises(SystemExit, match="Unrecognized TRADING_MODE"):
        resolve_mode("prod")
    assert confirm_live("ENABLE LIVE TRADING\n", is_tty=True) is True
    assert confirm_live("ENABLE LIVE TRADING\n", is_tty=False) is False
    assert confirm_live("enable live trading\n", is_tty=True) is False
    assert confirm_live("ENABLE LIVE TRADING \n", is_tty=True) is False


def test_quiet_hours_window_and_second_line(floor) -> None:
    quiet = datetime(2026, 11, 2, 23, 30, tzinfo=ET)
    awake = datetime(2026, 11, 2, 12, 0, tzinfo=ET)
    assert in_quiet_hours(quiet, "23:00", "07:00") is True
    assert in_quiet_hours(datetime(2026, 11, 2, 23, 0, tzinfo=ET), "23:00", "07:00") is True
    assert in_quiet_hours(datetime(2026, 11, 2, 7, 0, tzinfo=ET), "23:00", "07:00") is False
    assert in_quiet_hours(awake, "23:00", "07:00") is False

    entry = evaluate_risk(entry_intent(), floor, now=quiet, quote=fresh_quote(quiet))
    assert entry["passed"] is False
    assert any(rule["rule_id"] == "quiet_hours" and rule["passed"] is False for rule in entry["rules"])

    stop = entry_intent(side="sell", intent="stop", order_type="market", limit_price=None, stop=None, position_qty=Decimal("1"))
    checked = evaluate_risk(stop, floor, now=quiet, quote=fresh_quote(quiet))
    quiet_rule = next(rule for rule in checked["rules"] if rule["rule_id"] == "quiet_hours")
    assert quiet_rule["passed"] is True
    kept = discard_quiet_entries([entry_intent(), stop], quiet, floor)
    assert [item.intent for item in kept] == ["stop"]


def test_telegram_prefix_is_the_only_body() -> None:
    assert format_outbound("PAPER", "killed").startswith("[PAPER] ")
    assert format_outbound("LIVE", "killed").startswith("[LIVE] ")

    class Capture:
        def __init__(self) -> None:
            self.text = ""

        async def send_message(self, *, chat_id: str, text: str) -> None:
            self.text = text

    capture = Capture()

    import asyncio

    body = asyncio.run(deliver(capture, chat_id="1", mode="PAPER", text="halted"))
    assert body == "[PAPER] halted"
    assert capture.text == body


def test_signoff_canonical_vector() -> None:
    import hashlib
    import hmac

    fields = {
        "signoff_id": "00000000-0000-4000-8000-000000000001",
        "decision_id": "00000000-0000-4000-8000-000000000002",
        "intent_sha256": "abc",
        "risk_yaml_sha256": "def",
        "mode": "PAPER",
        "venue": "paper_engine",
        "symbol": "BTC-USD",
        "side": "buy",
        "qty": "0.1",
        "limit_price": "100",
        "intent": "entry",
        "expires_at": "2026-11-02T23:00:00.000000Z",
    }
    raw = canonical_bytes(fields)
    assert hmac.new(b"risk-test-key", raw, hashlib.sha256).hexdigest() == (
        "933e338ed2608b5362636a1aaf91b39ff01b420f646ea383ad2ef4b2303bd246"
    )


def test_stale_quote_and_market_entry_fail(floor, now) -> None:
    from datetime import timedelta

    stale = fresh_quote(now - timedelta(seconds=61))
    checked = evaluate_risk(entry_intent(), floor, now=now, quote=stale)
    assert checked["passed"] is False
    market = entry_intent(order_type="market", limit_price=None)
    checked = evaluate_risk(market, floor, now=now, quote=fresh_quote(now))
    assert checked["passed"] is False
    missing_stop = entry_intent(stop=None)
    checked = evaluate_risk(missing_stop, floor, now=now, quote=fresh_quote(now))
    assert checked["passed"] is False
