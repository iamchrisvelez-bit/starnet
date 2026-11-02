"""Execution process. Paper by default. LIVE waits on a TTY after reconciliation cancel."""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timezone

from tf_config.load import load_floor
from tf_execution.mode import confirm_live, resolve_mode
from tf_execution.paper import PaperEngine
from tf_execution.permissions import assert_permissions, map_permission_payload
from tf_execution.runtime import ExecutionRuntime


def build_runtime() -> ExecutionRuntime:
    mode = resolve_mode(os.environ.get("TRADING_MODE"))
    config = load_floor()
    paper = PaperEngine(maker_bps=None, taker_bps=None)
    report = map_permission_payload("paper_engine", paper.account_permissions())
    assert_permissions(report)
    venues = config.venues["venues"]
    for name, spec in venues.items():
        if name == "paper_engine":
            continue
        if spec.get("trade_enabled"):
            raise SystemExit(f"Refusing to start: {name} did not expose key permissions.")
    risk_key = os.environ.get("RISK_TOKEN_KEY", "")
    compliance_key = os.environ.get("COMPLIANCE_TOKEN_KEY", "")
    if not risk_key or not compliance_key:
        raise SystemExit("Refusing to start: sign-off keys are unset")
    runtime = ExecutionRuntime(
        mode=mode,
        live_confirmed=False,
        paper=paper,
        risk_key=risk_key.encode(),
        compliance_key=compliance_key.encode(),
        risk_yaml_sha256=config.risk_yaml_sha256,
        quote_max_age_sec=int(config.risk["crypto"]["quote_max_age_sec"]),
        heartbeat_block_sec=int(config.risk["shared"]["heartbeat_block_sec"]),
        heartbeat_cancel_sec=int(config.risk["shared"]["heartbeat_cancel_sec"]),
    )
    runtime.boot(datetime.now(timezone.utc))
    if mode == "LIVE" and sys.stdin.isatty():
        print("Type ENABLE LIVE TRADING to allow orders", flush=True)
        runtime.live_confirmed = confirm_live(sys.stdin.readline(), is_tty=True)
    return runtime


def main() -> None:
    runtime = build_runtime()
    while True:
        now = datetime.now(timezone.utc)
        runtime.note_beat("execution", now)
        runtime.tick(now)
        time.sleep(5)


if __name__ == "__main__":
    main()
