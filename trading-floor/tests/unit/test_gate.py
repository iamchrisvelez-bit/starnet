"""Phase 0 gate: paper account, KILL, dead-man, permission refusal."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest

from tf_execution.commands import apply_command
from tf_execution.permissions import assert_permissions, map_permission_payload
from tf_execution.runtime import OrderBlocked
from tests.support import entry_intent, fresh_quote, make_runtime, sign_pair


def test_paper_account_connects_and_rests_an_order(floor, now, runtime) -> None:
    report = map_permission_payload("paper_engine", runtime.paper.account_permissions())
    assert_permissions(report)
    health = runtime.paper.health()
    assert health["connected"] is True
    assert health["venue"] == "paper_engine"

    intent = entry_intent()
    risk, compliance = sign_pair(intent, floor, now)
    status = runtime.submit(intent, risk=risk, compliance=compliance, now=now, quote=fresh_quote(now))
    assert status.status == "acked"
    assert status.client_order_id.startswith("tf_")
    assert status.client_order_id in runtime.paper.open_orders


def test_kill_cancels_ours_and_blocks_new_orders_including_protective(floor, now, runtime) -> None:
    intent = entry_intent()
    risk, compliance = sign_pair(intent, floor, now)
    status = runtime.submit(intent, risk=risk, compliance=compliance, now=now, quote=fresh_quote(now))
    runtime.paper.seed_foreign("someone-elses-order")

    report = apply_command(runtime, "kill", now)
    assert status.client_order_id in report.cancelled
    assert "someone-elses-order" in report.left_alone
    assert "someone-elses-order" in runtime.paper.foreign
    assert status.client_order_id not in runtime.paper.open_orders

    stop = entry_intent(
        decision_id=intent.decision_id,
        side="sell",
        intent="stop",
        order_type="market",
        limit_price=None,
        stop=None,
        position_qty=Decimal("0.1"),
    )
    stop_risk, stop_compliance = sign_pair(stop, floor, now)
    with pytest.raises(OrderBlocked) as blocked:
        runtime.submit(stop, risk=stop_risk, compliance=stop_compliance, now=now, quote=fresh_quote(now))
    assert blocked.value.reason == "kill"
    assert apply_command(runtime, "resume", now) is None
    assert runtime.halted is True


def test_deadman_cancels_after_two_minutes_and_fifteen_seconds_only_halts(floor, now) -> None:
    runtime = make_runtime(floor, now)
    intent = entry_intent()
    risk, compliance = sign_pair(intent, floor, now)
    status = runtime.submit(intent, risk=risk, compliance=compliance, now=now, quote=fresh_quote(now))

    later = now + timedelta(seconds=20)
    runtime.note_beat("data", later)
    runtime.note_beat("risk", later)
    runtime.note_beat("execution", later)
    runtime.note_beat("scheduler", now)
    entry = entry_intent()
    entry_risk, entry_compliance = sign_pair(entry, floor, later)
    with pytest.raises(OrderBlocked) as blocked:
        runtime.submit(entry, risk=entry_risk, compliance=entry_compliance, now=later, quote=fresh_quote(later))
    assert blocked.value.reason == "heartbeat"
    assert status.client_order_id in runtime.paper.open_orders

    stop = entry_intent(side="sell", intent="stop", order_type="market", limit_price=None, stop=None, position_qty=Decimal("1"))
    stop_risk, stop_compliance = sign_pair(stop, floor, later)
    runtime.paper.taker_bps = Decimal("20")
    protective = runtime.submit(stop, risk=stop_risk, compliance=stop_compliance, now=later, quote=fresh_quote(later))
    assert protective.status == "filled"

    dead = now + timedelta(seconds=120)
    runtime.note_beat("data", now)
    runtime.note_beat("risk", now)
    runtime.note_beat("execution", now)
    runtime.note_beat("scheduler", now)
    level_runtime = make_runtime(floor, now)
    resting = entry_intent()
    resting_risk, resting_compliance = sign_pair(resting, floor, now)
    resting_status = level_runtime.submit(
        resting, risk=resting_risk, compliance=resting_compliance, now=now, quote=fresh_quote(now)
    )
    level_runtime.tick(dead)
    assert resting_status.client_order_id not in level_runtime.paper.open_orders


def test_withdrawal_bit_and_missing_permissions_refuse_startup() -> None:
    withdrawal = map_permission_payload(
        "coinbase_advanced",
        {"can_trade": True, "can_withdraw": True, "can_transfer": False, "eligibility_ok": True},
    )
    with pytest.raises(SystemExit, match="Refusing to start: coinbase_advanced key reports withdrawal or transfer permission."):
        assert_permissions(withdrawal)

    transfer = map_permission_payload(
        "kraken",
        {"can_trade": True, "can_withdraw": False, "can_transfer": True, "eligibility_ok": True},
    )
    with pytest.raises(SystemExit, match="Refusing to start: kraken key reports withdrawal or transfer permission."):
        assert_permissions(transfer)

    omitted = map_permission_payload("alpaca_crypto", {"can_trade": True})
    with pytest.raises(SystemExit, match="Refusing to start: alpaca_crypto did not expose key permissions."):
        assert_permissions(omitted)

    unknown_shape = map_permission_payload("kraken", {"result": {"rights": "query"}})
    with pytest.raises(SystemExit, match="Refusing to start: kraken did not expose key permissions."):
        assert_permissions(unknown_shape)

    trade_only = map_permission_payload(
        "paper_engine",
        {"can_trade": True, "can_withdraw": False, "can_transfer": False, "eligibility_ok": True},
    )
    assert_permissions(trade_only)


def test_live_without_confirmation_blocks_orders(floor, now) -> None:
    runtime = make_runtime(floor, now, mode="LIVE", live_confirmed=False)
    intent = entry_intent()
    risk, compliance = sign_pair(intent, floor, now)
    with pytest.raises(OrderBlocked) as blocked:
        runtime.submit(intent, risk=risk, compliance=compliance, now=now, quote=fresh_quote(now))
    assert blocked.value.reason == "live_unconfirmed"


def test_boot_cancels_ours_before_submit(floor, now) -> None:
    from tf_execution.paper import PaperEngine
    from tf_execution.runtime import ExecutionRuntime

    paper = PaperEngine(maker_bps=None, taker_bps=None)
    paper.submit(entry_intent(), "tf_boot:1", fresh_quote(now))
    paper.seed_foreign("foreign-boot")
    runtime = ExecutionRuntime(
        mode="PAPER",
        live_confirmed=False,
        paper=paper,
        risk_key=b"risk-test-key",
        compliance_key=b"compliance-test-key",
        risk_yaml_sha256=floor.risk_yaml_sha256,
        quote_max_age_sec=60,
        heartbeat_block_sec=15,
        heartbeat_cancel_sec=120,
    )
    report = runtime.boot(now)
    assert "tf_boot:1" in report.cancelled
    assert "foreign-boot" in report.left_alone
