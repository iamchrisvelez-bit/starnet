"""Telegram process. Messages go through format_outbound. No send when the token is unset."""

from __future__ import annotations

import os
import time

from tf_execution.mode import resolve_mode


def main() -> None:
    mode = resolve_mode(os.environ.get("TRADING_MODE"))
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    while True:
        _ = (mode, bool(token))
        time.sleep(5)


if __name__ == "__main__":
    main()
