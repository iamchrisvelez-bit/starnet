"""Scheduler publishes ticks. It does not call a venue."""

from __future__ import annotations

import os
import time

from tf_execution.mode import resolve_mode
from tf_scheduler.ticks import heartbeat, schedule_tick


def main() -> None:
    mode = resolve_mode(os.environ.get("TRADING_MODE"))
    while True:
        _ = (heartbeat(mode), schedule_tick(mode, "guard"))
        time.sleep(5)


if __name__ == "__main__":
    main()
