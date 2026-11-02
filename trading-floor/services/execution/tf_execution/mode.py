"""Mode is a property of this process. It is not inferred from which keys exist."""

from __future__ import annotations

LIVE_PHRASE = "ENABLE LIVE TRADING"


def resolve_mode(raw: str | None) -> str:
    if raw is None or raw.strip() == "" or raw.strip().lower() == "paper":
        return "PAPER"
    if raw.strip().lower() == "live":
        return "LIVE"
    raise SystemExit("Unrecognized TRADING_MODE")


def confirm_live(line: str, *, is_tty: bool) -> bool:
    """Only a TTY and the exact phrase count. Pipes, env, web, and Telegram do not."""

    if not is_tty:
        return False
    return line.strip("\r\n") == LIVE_PHRASE
