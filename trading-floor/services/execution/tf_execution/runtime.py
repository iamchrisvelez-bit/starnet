"""Kill, pause, dead-man, and the paper submit path."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

from tf_journal.chain import JournalStore
from tf_models.journal import JournalKind
from tf_models.market import Quote
from tf_models.orders import CancelReport, OrderIntent, OrderStatus
from tf_models.signoff import ComplianceSignOff, RiskSignOff
from tf_execution.paper import PaperEngine
from tf_execution.signoff_verify import verify_compliance, verify_risk
from tf_execution.watchdog import BeatLevel, assess
from tf_risk.quotes import quote_is_stale


class OrderBlocked(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


PROTECTIVE = frozenset({"exit", "stop", "reduce", "guard_derisk"})


def client_order_id(decision_id: UUID, seq: int) -> str:
    return f"tf_{decision_id}:{seq}"


@dataclass
class ExecutionRuntime:
    mode: str
    live_confirmed: bool
    paper: PaperEngine
    risk_key: bytes
    compliance_key: bytes
    risk_yaml_sha256: str
    quote_max_age_sec: int
    heartbeat_block_sec: int
    heartbeat_cancel_sec: int
    journal: JournalStore | None = None
    halted: bool = False
    paused: bool = False
    started_at: datetime | None = None
    beats: dict[str, datetime | None] = field(default_factory=dict)
    used_signoffs: set[str] = field(default_factory=set)
    booted: bool = False
    _seq: int = 0

    def boot(self, now: datetime, *, persisted_halt: bool = False) -> CancelReport:
        """Reconciliation cancel runs before any submit. LIVE stays unconfirmed until a TTY phrase."""

        self.started_at = now.astimezone(timezone.utc)
        self.halted = persisted_halt
        report = self.paper.cancel_all_ours()
        self.booted = True
        self._journal(JournalKind.command, None, {"action": "boot_cancel", "cancelled": report.cancelled})
        return report

    def note_beat(self, service: str, ts: datetime) -> None:
        self.beats[service] = ts

    def kill(self, now: datetime) -> CancelReport:
        self.halted = True
        report = self.paper.cancel_all_ours()
        self._journal(
            JournalKind.command,
            None,
            {"action": "kill", "cancelled": report.cancelled, "left_alone": report.left_alone},
        )
        return report

    def pause(self, now: datetime) -> None:
        self.paused = True
        self._journal(JournalKind.command, None, {"action": "pause"})

    def resume(self) -> bool:
        """Clears a manual pause only. Kill, permission failure, and loss latches stay."""

        if self.halted:
            return False
        self.paused = False
        self._journal(JournalKind.command, None, {"action": "resume"})
        return True

    def tick(self, now: datetime) -> BeatLevel:
        if self.started_at is None:
            raise OrderBlocked("not_booted")
        level = assess(
            self.beats,
            now,
            started_at=self.started_at,
            block_sec=self.heartbeat_block_sec,
            cancel_sec=self.heartbeat_cancel_sec,
        )
        if level is BeatLevel.CANCEL:
            self.paper.cancel_all_ours()
            self._journal(JournalKind.guard, None, {"action": "deadman_cancel"})
        return level

    def submit(
        self,
        intent: OrderIntent,
        *,
        risk: RiskSignOff,
        compliance: ComplianceSignOff,
        now: datetime,
        quote: Quote | None,
    ) -> OrderStatus:
        if not self.booted:
            raise OrderBlocked("not_booted")
        if self.halted:
            raise OrderBlocked("kill")
        if self.mode == "LIVE" and not self.live_confirmed:
            raise OrderBlocked("live_unconfirmed")
        if self.mode == "PAPER" and intent.venue != "paper_engine":
            raise OrderBlocked("paper_venue")
        if intent.decision_id is None:
            raise OrderBlocked("missing_decision_id")
        level = self.tick(now)
        if level is BeatLevel.CANCEL:
            raise OrderBlocked("deadman")
        protective = intent.intent in PROTECTIVE
        if level is BeatLevel.HALT_ALL or (level is BeatLevel.HALT_ENTRIES and not protective):
            raise OrderBlocked("heartbeat")
        if self.paused and not protective:
            raise OrderBlocked("pause")
        if quote is not None and quote_is_stale(quote, now, max_age_sec=self.quote_max_age_sec):
            raise OrderBlocked("stale_quote")
        if quote is None:
            raise OrderBlocked("stale_quote")
        if not verify_risk(intent, risk, key=self.risk_key, mode=self.mode, now=now, risk_yaml_sha256=self.risk_yaml_sha256):
            raise OrderBlocked("risk_signoff")
        if not verify_compliance(
            intent,
            compliance,
            key=self.compliance_key,
            mode=self.mode,
            now=now,
            risk_yaml_sha256=self.risk_yaml_sha256,
        ):
            raise OrderBlocked("compliance_signoff")
        pair = (str(risk.signoff_id), str(compliance.signoff_id))
        if pair[0] in self.used_signoffs or pair[1] in self.used_signoffs:
            raise OrderBlocked("signoff_reused")
        self.used_signoffs.add(pair[0])
        self.used_signoffs.add(pair[1])
        self._seq += 1
        coid = client_order_id(intent.decision_id, self._seq)
        status = self.paper.submit(intent, coid, quote)
        self._journal(
            JournalKind.order_submitted,
            intent.decision_id,
            {"client_order_id": coid, "symbol": intent.symbol, "side": intent.side, "status": status.status},
        )
        return status

    def _journal(self, kind: JournalKind, decision_id: UUID | None, payload: dict) -> None:
        if self.journal is None:
            return
        self.journal.append(
            kind=kind,
            actor="execution",
            mode=self.mode,
            payload=payload,
            ts_utc=datetime.now(timezone.utc),
            decision_id=decision_id,
        )
