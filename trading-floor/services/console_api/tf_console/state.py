from __future__ import annotations

from dataclasses import dataclass, field

from tf_bus.memory import InMemoryBus
from tf_models.bus import StreamName


@dataclass
class ConsoleState:
    mode: str = "PAPER"
    live_confirmed: bool = False
    halted: bool = False
    paused: bool = False
    bus: InMemoryBus = field(default_factory=InMemoryBus)

    def publish_command(self, action: str) -> None:
        from datetime import datetime, timezone
        from uuid import uuid4

        self.bus.publish(
            StreamName.COMMANDS,
            {
                "event_id": str(uuid4()),
                "decision_id": str(uuid4()),
                "type": "command",
                "producer": "console_api",
                "schema_version": 1,
                "mode": self.mode,
                "ts_utc": datetime.now(timezone.utc).isoformat(),
                "payload": {"action": action},
            },
        )
