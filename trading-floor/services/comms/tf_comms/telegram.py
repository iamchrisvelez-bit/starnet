"""Every outbound Telegram body is built here, with the mode prefix."""

from __future__ import annotations

from typing import Literal, Protocol


def format_outbound(mode: Literal["PAPER", "LIVE"], text: str) -> str:
    if mode not in ("PAPER", "LIVE"):
        raise ValueError("mode must be PAPER or LIVE")
    return f"[{mode}] {text}"


class Sender(Protocol):
    async def send_message(self, *, chat_id: str, text: str) -> None: ...


async def deliver(sender: Sender, *, chat_id: str, mode: Literal["PAPER", "LIVE"], text: str) -> str:
    body = format_outbound(mode, text)
    await sender.send_message(chat_id=chat_id, text=body)
    return body
