"""Parsers for public Coinbase Exchange, Kraken, and Alpaca crypto payloads."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from tf_models.market import Quote


def parse_exchange_time(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    if "." in text:
        head, tail = text.split(".", 1)
        frac: list[str] = []
        index = 0
        while index < len(tail) and tail[index].isdigit():
            if len(frac) < 6:
                frac.append(tail[index])
            index += 1
        while len(frac) < 6:
            frac.append("0")
        text = f"{head}.{''.join(frac)}{tail[index:]}"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        raise ValueError("exchange time must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def parse_coinbase_ticker(symbol: str, payload: dict, *, received_at_utc: datetime) -> Quote:
    return Quote(
        venue="coinbase_advanced",
        symbol=symbol,
        bid=Decimal(str(payload["bid"])),
        ask=Decimal(str(payload["ask"])),
        last=Decimal(str(payload["price"])),
        ts_utc=parse_exchange_time(payload["time"]),
        received_at_utc=received_at_utc,
    )


def parse_kraken_ticker(symbol: str, result_key: str, payload: dict, *, received_at_utc: datetime) -> Quote:
    if payload.get("error"):
        raise ValueError("kraken error")
    row = payload["result"][result_key]
    last = Decimal(str(row["c"][0]))
    bid = Decimal(str(row["b"][0]))
    ask = Decimal(str(row["a"][0]))
    return Quote(
        venue="kraken",
        symbol=symbol,
        bid=bid,
        ask=ask,
        last=last,
        ts_utc=received_at_utc,
        received_at_utc=received_at_utc,
    )


def parse_alpaca_quote(symbol: str, pair: str, payload: dict, *, received_at_utc: datetime) -> Quote:
    row = payload["quotes"][pair]
    bid = Decimal(str(row["bp"]))
    ask = Decimal(str(row["ap"]))
    last = (bid + ask) / Decimal("2")
    return Quote(
        venue="alpaca_crypto",
        symbol=symbol,
        bid=bid,
        ask=ask,
        last=last,
        ts_utc=parse_exchange_time(row["t"]),
        received_at_utc=received_at_utc,
    )
