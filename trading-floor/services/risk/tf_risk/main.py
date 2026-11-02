"""Risk process heartbeats. It does not place orders and does not write risk.yaml."""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone

from tf_config.load import load_floor
from tf_execution.mode import resolve_mode


def main() -> None:
    mode = resolve_mode(os.environ.get("TRADING_MODE"))
    config = load_floor()
    while True:
        _ = (mode, config.risk_yaml_sha256, datetime.now(timezone.utc))
        time.sleep(5)


if __name__ == "__main__":
    main()
