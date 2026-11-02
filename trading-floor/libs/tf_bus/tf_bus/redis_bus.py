"""Redis Streams client. Consumers resume from the last ack. Fails closed if Redis is down."""

from __future__ import annotations

import json
from typing import Any

from tf_bus.protocol import accept_message
from tf_models.bus import StreamName


class RedisBus:
    def __init__(self, client: Any) -> None:
        self._client = client

    def publish(self, stream: str, raw: dict) -> bool:
        message, reason = accept_message(raw)
        target = stream if message is not None else StreamName.DEAD
        body = raw if message is None else message.model_dump(mode="json")
        if message is None:
            body = {"reason": reason, "payload": json.dumps(raw, default=str)}
        self._client.xadd(target, {"data": json.dumps(body, default=str)})
        return message is not None

    def ensure_group(self, stream: str, group: str) -> None:
        try:
            self._client.xgroup_create(stream, group, id="0", mkstream=True)
        except Exception as exc:  # BUSYGROUP is the resume path
            if "BUSYGROUP" not in str(exc):
                raise

    def read_group(self, stream: str, group: str, consumer: str, *, count: int = 50) -> list[tuple[str, dict]]:
        rows = self._client.xreadgroup(group, consumer, {stream: ">"}, count=count)
        found: list[tuple[str, dict]] = []
        for _stream, messages in rows or []:
            for message_id, fields in messages:
                data = fields.get("data") or fields.get(b"data")
                if isinstance(data, bytes):
                    data = data.decode()
                found.append((message_id, json.loads(data)))
        return found

    def ack(self, stream: str, group: str, message_id: str) -> None:
        self._client.xack(stream, group, message_id)
