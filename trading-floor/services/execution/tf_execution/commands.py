"""Apply a bus command. The console publishes; only execution cancels."""

from __future__ import annotations

from datetime import datetime

from tf_execution.runtime import ExecutionRuntime
from tf_models.orders import CancelReport


def apply_command(runtime: ExecutionRuntime, action: str, now: datetime) -> CancelReport | None:
    if action == "kill":
        return runtime.kill(now)
    if action == "pause":
        runtime.pause(now)
        return None
    if action == "resume":
        runtime.resume()
        return None
    raise ValueError(f"unknown command {action}")
