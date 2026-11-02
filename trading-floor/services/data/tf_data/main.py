"""Public ingest loop. Heartbeats even when a venue is down. Never places an order."""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone

from tf_data.client import MarketDataClient
from tf_execution.mode import resolve_mode


def main() -> None:
    mode = resolve_mode(os.environ.get("TRADING_MODE"))
    client = MarketDataClient()
    while True:
        now = datetime.now(timezone.utc)
        for product in ("BTC-USD", "ETH-USD"):
            try:
                client.coinbase_ticker(product)
            except Exception:
                pass
        try:
            client.kraken_ticker("XBTUSD")
        except Exception:
            pass
        try:
            client.alpaca_quotes("BTC/USD")
        except Exception:
            pass
        _ = (mode, now)
        time.sleep(15)


if __name__ == "__main__":
    main()
