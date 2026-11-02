"""Market-data HTTP. Order paths and the live Alpaca trade host are refused."""

from __future__ import annotations

import httpx

COINBASE_PUBLIC = "https://api.exchange.coinbase.com"
KRAKEN_PUBLIC = "https://api.kraken.com"
ALPACA_DATA = "https://data.alpaca.markets"
ALPACA_LIVE_TRADE = "https://api.alpaca.markets"


class MarketDataClient:
    """Read-only. Phase 0 never builds an order request."""

    def __init__(self, transport: httpx.BaseTransport | None = None) -> None:
        self._client = httpx.Client(transport=transport, timeout=10.0)

    def close(self) -> None:
        self._client.close()

    def get_json(self, url: str) -> dict:
        if url.startswith(ALPACA_LIVE_TRADE):
            raise RuntimeError("Refusing to call the live Alpaca host")
        path = httpx.URL(url).path.lower()
        if "order" in path:
            raise RuntimeError("Refusing to call an order path from data")
        response = self._client.get(url)
        response.raise_for_status()
        body = response.json()
        if not isinstance(body, dict):
            raise ValueError("market data payload must be an object")
        return body

    def coinbase_ticker(self, product: str) -> dict:
        return self.get_json(f"{COINBASE_PUBLIC}/products/{product}/ticker")

    def kraken_ticker(self, pair: str) -> dict:
        return self.get_json(f"{KRAKEN_PUBLIC}/0/public/Ticker?pair={pair}")

    def alpaca_quotes(self, symbols: str) -> dict:
        return self.get_json(f"{ALPACA_DATA}/v1beta3/crypto/us/latest/quotes?symbols={symbols}")
