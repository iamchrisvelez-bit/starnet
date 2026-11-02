from __future__ import annotations

from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from tf_models.common import UtcDatetime


class JournalKind(str, Enum):
    signal = "signal"
    context_check = "context_check"
    research_finding = "research_finding"
    argument = "argument"
    debate_request = "debate_request"
    daily_plan = "daily_plan"
    allocation = "allocation"
    trade_decision = "trade_decision"
    agent_output_rejected = "agent_output_rejected"
    audit_report = "audit_report"
    risk_check = "risk_check"
    compliance_check = "compliance_check"
    risk_signoff = "risk_signoff"
    compliance_signoff = "compliance_signoff"
    approval = "approval"
    order_submitted = "order_submitted"
    order_acked = "order_acked"
    order_rejected = "order_rejected"
    cancel = "cancel"
    fill = "fill"
    guard = "guard"
    heartbeat = "heartbeat"
    playbook_proposal = "playbook_proposal"
    promotion = "promotion"
    demotion = "demotion"
    config_revision = "config_revision"
    escalation = "escalation"
    moonit_curve = "moonit_curve"
    moonit_quote = "moonit_quote"
    moonit_simulation = "moonit_simulation"
    moonit_signature = "moonit_signature"
    caller_observation = "caller_observation"
    lesson = "lesson"
    mode_change = "mode_change"
    command = "command"


class JournalEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    journal_id: UUID
    decision_id: UUID | None
    parent_decision_id: UUID | None = None
    ts_utc: UtcDatetime
    mode: Literal["PAPER", "LIVE"]
    kind: JournalKind
    actor: str
    schema_version: int = Field(default=1, ge=1)
    payload: dict
    prev_hash: str
    hash: str
