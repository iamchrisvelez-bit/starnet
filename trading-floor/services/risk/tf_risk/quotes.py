from __future__ import annotations

from datetime import datetime, timedelta

from tf_models.market import Quote


def quote_is_stale(quote: Quote, now: datetime, *, max_age_sec: int) -> bool:
    """Fail closed when the exchange/receive gap or the local age exceeds the config limit."""

    if now.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware UTC")
    limit = timedelta(seconds=max_age_sec)
    exchange_gap = quote.received_at_utc - quote.ts_utc
    local_age = now - quote.received_at_utc
    from_exchange = now - quote.ts_utc
    return exchange_gap > limit or local_age > limit or from_exchange > limit
