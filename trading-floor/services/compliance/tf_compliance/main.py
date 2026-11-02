"""Compliance process. Read-only config. No venue calls."""

from __future__ import annotations

import os
import time

from tf_config.load import load_floor
from tf_execution.mode import resolve_mode


def main() -> None:
    mode = resolve_mode(os.environ.get("TRADING_MODE"))
    load_floor()
    while True:
        _ = mode
        time.sleep(5)


if __name__ == "__main__":
    main()
