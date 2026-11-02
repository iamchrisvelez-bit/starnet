"""Parquet via DuckDB. Quotes are data, not orders."""

from __future__ import annotations

from pathlib import Path

import duckdb

from tf_models.market import Quote


def write_quotes(path: Path, quotes: list[Quote]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        (
            quote.venue,
            quote.symbol,
            None if quote.bid is None else str(quote.bid),
            None if quote.ask is None else str(quote.ask),
            str(quote.last),
            quote.ts_utc.isoformat(),
            quote.received_at_utc.isoformat(),
        )
        for quote in quotes
    ]
    connection = duckdb.connect()
    try:
        connection.execute(
            """
            CREATE TABLE quotes (
                venue VARCHAR, symbol VARCHAR, bid VARCHAR, ask VARCHAR,
                last VARCHAR, ts_utc VARCHAR, received_at_utc VARCHAR
            )
            """
        )
        connection.executemany("INSERT INTO quotes VALUES (?, ?, ?, ?, ?, ?, ?)", rows)
        connection.execute(f"COPY quotes TO '{path.as_posix()}' (FORMAT PARQUET)")
    finally:
        connection.close()


def read_symbols(path: Path) -> list[str]:
    connection = duckdb.connect()
    try:
        rows = connection.execute(
            "SELECT DISTINCT symbol FROM read_parquet(?)",
            [path.as_posix()],
        ).fetchall()
    finally:
        connection.close()
    return [row[0] for row in rows]
