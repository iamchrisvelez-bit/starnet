"""Shared types. Money is Decimal. Timestamps are timezone-aware UTC."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated

from pydantic import AfterValidator, PlainSerializer

def _aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise ValueError("timestamps must be timezone-aware UTC")
    return value.astimezone(timezone.utc)


def format_ts(value: datetime) -> str:
    aware = _aware_utc(value)
    return aware.strftime("%Y-%m-%dT%H:%M:%S.") + f"{aware.microsecond:06d}Z"


def decimal_str(value: Decimal | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered or "0"


UtcDatetime = Annotated[datetime, AfterValidator(_aware_utc)]
Money = Annotated[Decimal, PlainSerializer(lambda value: decimal_str(value), return_type=str)]
