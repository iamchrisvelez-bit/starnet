"""REST and WebSocket for the console. There is no order endpoint and no mode switch."""

from __future__ import annotations

import os
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ConfigDict

from tf_config.load import load_floor
from tf_console.state import ConsoleState
from tf_risk.quiet import in_quiet_hours

app = FastAPI(title="Trading Floor console", version="0.1.0")
STATE = ConsoleState(mode=os.environ.get("TF_CONSOLE_MODE", "PAPER"))


class CommandBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str | None = None


def _read_token() -> str:
    token = os.environ.get("CONSOLE_READ_TOKEN", "")
    if not token:
        raise HTTPException(status_code=503, detail="CONSOLE_READ_TOKEN is not set")
    return token


def _command_token() -> str:
    token = os.environ.get("CONSOLE_COMMAND_TOKEN", "")
    if not token:
        raise HTTPException(status_code=503, detail="CONSOLE_COMMAND_TOKEN is not set")
    return token


def require_read(authorization: str | None = Header(default=None)) -> None:
    expected = _read_token()
    if authorization != f"Bearer {expected}":
        raise HTTPException(status_code=401, detail="read token required")


def require_command(authorization: str | None = Header(default=None)) -> None:
    command = _command_token()
    read = os.environ.get("CONSOLE_READ_TOKEN", "")
    if authorization == f"Bearer {read}" and read and read != command:
        raise HTTPException(status_code=403, detail="command token required")
    if authorization != f"Bearer {command}":
        raise HTTPException(status_code=401, detail="command token required")


def mode_payload() -> dict:
    return {
        "mode": STATE.mode,
        "live_confirmed": STATE.live_confirmed,
        "halted": STATE.halted,
        "paused": STATE.paused,
    }


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True, "mode": STATE.mode}


@app.get("/api/v1/mode")
def get_mode(_: None = Depends(require_read)) -> dict:
    return mode_payload()


@app.get("/api/v1/floor")
def floor(_: None = Depends(require_read)) -> dict:
    return {"stations": []}


@app.get("/api/v1/desks")
def desks(_: None = Depends(require_read)) -> dict:
    return {"desks": []}


@app.get("/api/v1/positions")
def positions(_: None = Depends(require_read)) -> dict:
    return {"positions": []}


@app.get("/api/v1/orders")
def orders(_: None = Depends(require_read)) -> dict:
    return {"orders": []}


@app.get("/api/v1/fills")
def fills(_: None = Depends(require_read)) -> dict:
    return {"fills": []}


@app.get("/api/v1/approvals")
def approvals(_: None = Depends(require_read)) -> dict:
    return {"approvals": []}


@app.get("/api/v1/equity")
def equity(_: None = Depends(require_read)) -> dict:
    return {"equity": None, "benchmark": "BTC"}


@app.get("/api/v1/guards")
def guards(_: None = Depends(require_read)) -> dict:
    config = load_floor()
    now = datetime.now(timezone.utc)
    start = str(config.approvals["quiet_hours_start_et"])
    end = str(config.approvals["quiet_hours_end_et"])
    return {
        "quiet_hours": in_quiet_hours(now, start, end),
        "quiet_hours_start_et": start,
        "quiet_hours_end_et": end,
        "approval_mode": config.approvals["approval_mode"],
        "halted": STATE.halted,
        "paused": STATE.paused,
        "deadman_cancel_sec": config.risk["shared"]["heartbeat_cancel_sec"],
        "mode": STATE.mode,
    }


def _command(action: str) -> dict:
    if action == "kill":
        STATE.halted = True
    elif action == "pause":
        STATE.paused = True
    elif action == "resume":
        if not STATE.halted:
            STATE.paused = False
    else:
        raise HTTPException(status_code=400, detail="unknown command")
    STATE.publish_command(action)
    return mode_payload()


@app.post("/api/v1/commands/kill")
def kill(_: None = Depends(require_command)) -> dict:
    return _command("kill")


@app.post("/api/v1/commands/pause")
def pause(_: None = Depends(require_command)) -> dict:
    return _command("pause")


@app.post("/api/v1/commands/resume")
def resume(_: None = Depends(require_command)) -> dict:
    return _command("resume")


@app.websocket("/api/v1/stream")
async def stream(websocket: WebSocket) -> None:
    token = websocket.query_params.get("read_token", "")
    expected = os.environ.get("CONSOLE_READ_TOKEN", "")
    if not expected or token != expected:
        await websocket.close(code=4401)
        return
    await websocket.accept()
    await websocket.send_json({"type": "mode", **mode_payload()})
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        return
