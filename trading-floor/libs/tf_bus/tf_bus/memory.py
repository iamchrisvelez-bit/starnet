"""In-memory stand-in for Redis Streams consumer groups. RedisBus is the process client."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from tf_bus.protocol import accept_message
from tf_models.bus import BusMessage


@dataclass
class InMemoryBus:
    streams: dict[str, list[BusMessage]] = field(default_factory=lambda: defaultdict(list))
    dead: list[dict] = field(default_factory=list)
    acked: dict[tuple[str, str], set[str]] = field(default_factory=lambda: defaultdict(set))

    def publish(self, stream: str, raw: dict) -> BusMessage | None:
        message, reason = accept_message(raw)
        if message is None:
            self.dead.append({"stream": stream, "reason": reason, "raw_type": raw.get("type")})
            return None
        self.streams[stream].append(message)
        return message

    def read_new(self, stream: str, group: str) -> list[BusMessage]:
        seen = self.acked[(stream, group)]
        pending = [message for message in self.streams.get(stream, []) if str(message.event_id) not in seen]
        return pending

    def ack(self, stream: str, group: str, event_id: str) -> None:
        self.acked[(stream, group)].add(event_id)
