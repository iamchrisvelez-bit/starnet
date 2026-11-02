from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from tf_data.client import ALPACA_DATA, ALPACA_LIVE_TRADE, MarketDataClient
from tf_data.parse import parse_alpaca_quote, parse_coinbase_ticker, parse_kraken_ticker
from tf_data.store import read_symbols, write_quotes
from tf_execution.paper import FeeScheduleMissing, PaperEngine
from tf_scheduler.jobs import build_scheduler
from tests.support import entry_intent, fresh_quote

ROOT = Path(__file__).resolve().parents[2]


def test_public_payloads_parse() -> None:
    received = datetime(2026, 11, 2, 22, 19, tzinfo=timezone.utc)
    coinbase = {
        "ask": "76828.17",
        "bid": "76828.16",
        "price": "76828.16",
        "time": "2026-11-02T22:18:25.682914735Z",
    }
    quote = parse_coinbase_ticker("BTC-USD", coinbase, received_at_utc=received)
    assert quote.bid is not None and quote.ask is not None
    assert quote.ts_utc.microsecond == 682914

    kraken = {"error": [], "result": {"XXBTZUSD": {"a": ["76838.00000", "6", "6"], "b": ["76837.90000", "1", "1"], "c": ["76838.00000", "0.001"]}}}
    parsed = parse_kraken_ticker("BTC-USD", "XXBTZUSD", kraken, received_at_utc=received)
    assert parsed.venue == "kraken"
    assert parsed.last == parsed.ask

    alpaca = {"quotes": {"BTC/USD": {"ap": 76870.48, "bp": 76853.385, "t": "2026-11-02T22:19:07.437892383Z"}}}
    aqua = parse_alpaca_quote("BTC-USD", "BTC/USD", alpaca, received_at_utc=received)
    assert aqua.venue == "alpaca_crypto"


def test_data_client_refuses_order_paths_and_live_host() -> None:
    client = MarketDataClient(transport=httpx.MockTransport(lambda request: (_ for _ in ()).throw(AssertionError(request.url))))
    with pytest.raises(RuntimeError, match="live Alpaca"):
        client.get_json(f"{ALPACA_LIVE_TRADE}/v2/orders")
    with pytest.raises(RuntimeError, match="order path"):
        client.get_json(f"{ALPACA_DATA}/v2/orders")
    client.close()


def test_parquet_roundtrip(tmp_path: Path) -> None:
    now = datetime(2026, 11, 2, 18, 0, tzinfo=timezone.utc)
    path = tmp_path / "quotes.parquet"
    write_quotes(path, [fresh_quote(now)])
    assert read_symbols(path) == ["BTC-USD"]


def test_unset_fee_refuses_a_crossing_fill() -> None:
    now = datetime(2026, 11, 2, 18, 0, tzinfo=timezone.utc)
    paper = PaperEngine(maker_bps=None, taker_bps=None)
    with pytest.raises(FeeScheduleMissing):
        paper.submit(entry_intent(limit_price=None, order_type="market"), "tf_fee:1", fresh_quote(now))


def test_duplicate_client_id_does_not_double_fill() -> None:
    from decimal import Decimal

    now = datetime(2026, 11, 2, 18, 0, tzinfo=timezone.utc)
    paper = PaperEngine(maker_bps=Decimal("10"), taker_bps=Decimal("20"))
    intent = entry_intent(order_type="market", limit_price=None)
    first = paper.submit(intent, "tf_dup:1", fresh_quote(now))
    second = paper.submit(intent, "tf_dup:1", fresh_quote(now))
    assert first.venue_order_id == second.venue_order_id
    assert len(paper.fills) == 1


def test_scheduler_jobs_are_ticks_only() -> None:
    scheduler = build_scheduler("PAPER")
    ids = {job.id for job in scheduler.get_jobs()}
    assert ids == {"daily_plan", "nightly_review", "heartbeat"}


def test_console_commands_and_mode_badge_api(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONSOLE_READ_TOKEN", "read-token")
    monkeypatch.setenv("CONSOLE_COMMAND_TOKEN", "command-token")
    monkeypatch.setenv("TF_CONSOLE_MODE", "PAPER")
    from tf_console import api

    api.STATE.mode = "PAPER"
    api.STATE.halted = False
    api.STATE.paused = False
    api.STATE.live_confirmed = False
    client = TestClient(api.app)
    assert client.get("/api/v1/mode").status_code == 401
    headers = {"Authorization": "Bearer read-token"}
    mode = client.get("/api/v1/mode", headers=headers)
    assert mode.json()["mode"] == "PAPER"
    denied = client.post("/api/v1/commands/kill", headers=headers)
    assert denied.status_code == 403
    killed = client.post("/api/v1/commands/kill", headers={"Authorization": "Bearer command-token"})
    assert killed.status_code == 200
    assert killed.json()["halted"] is True
    resumed = client.post("/api/v1/commands/resume", headers={"Authorization": "Bearer command-token"})
    assert resumed.json()["halted"] is True
    order_posts = [
        route
        for route in api.app.routes
        if getattr(route, "methods", None) and "POST" in route.methods and "order" in route.path
    ]
    assert order_posts == []
    with client.websocket_connect("/api/v1/stream?read_token=read-token") as socket:
        first = socket.receive_json()
    assert first["type"] == "mode"
    assert first["mode"] == "PAPER"


def test_no_secret_material_in_the_tree() -> None:
    import re

    patterns = (
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        re.compile(r"xoxb-[0-9]{8,}-[0-9A-Za-z]{16,}"),
        re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"),
    )
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".venv", "node_modules", "__pycache__"} for part in path.parts):
            continue
        if path.name == ".env":
            raise AssertionError(path)
        if path.suffix in {".png", ".parquet", ".lock"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in patterns:
            assert pattern.search(text) is None, path


def test_execution_source_does_not_mint_signoffs() -> None:
    blob = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "services" / "execution").rglob("*.py"))
    assert "mint_risk_signoff" not in blob
    assert "mint_compliance_signoff" not in blob


@pytest.mark.skipif(os.environ.get("TF_LIVE_PUBLIC_DATA") != "1", reason="set TF_LIVE_PUBLIC_DATA=1 to hit public books")
def test_live_public_books() -> None:
    client = MarketDataClient()
    try:
        coinbase = client.coinbase_ticker("BTC-USD")
        kraken = client.kraken_ticker("XBTUSD")
        alpaca = client.alpaca_quotes("BTC/USD")
    finally:
        client.close()
    received = datetime.now(timezone.utc)
    assert parse_coinbase_ticker("BTC-USD", coinbase, received_at_utc=received).last > 0
    assert parse_kraken_ticker("BTC-USD", "XXBTZUSD", kraken, received_at_utc=received).last > 0
    assert parse_alpaca_quote("BTC-USD", "BTC/USD", alpaca, received_at_utc=received).ask is not None
