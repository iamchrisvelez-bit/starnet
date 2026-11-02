"""Execution verifies tokens. It does not mint them."""

from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timezone

from tf_models.orders import OrderIntent
from tf_models.signoff import ComplianceSignOff, RiskSignOff, canonical_bytes
from tf_risk.check import signoff_fields


def _fresh(expires_at: datetime, now: datetime) -> bool:
    return expires_at.astimezone(timezone.utc) > now.astimezone(timezone.utc)


def verify_risk(intent: OrderIntent, signoff: RiskSignOff, *, key: bytes, mode: str, now: datetime, risk_yaml_sha256: str) -> bool:
    if signoff.mode != mode or signoff.decision_id != intent.decision_id:
        return False
    if signoff.risk_yaml_sha256 != risk_yaml_sha256:
        return False
    if not _fresh(signoff.expires_at_utc, now):
        return False
    if signoff.symbol != intent.symbol or signoff.side != intent.side or signoff.qty != intent.qty:
        return False
    if signoff.limit_price != intent.limit_price or signoff.intent != intent.intent or signoff.venue != intent.venue:
        return False
    fields = signoff_fields(
        signoff_id=signoff.signoff_id,
        intent=intent,
        intent_hash=signoff.intent_sha256,
        risk_yaml_sha256=signoff.risk_yaml_sha256,
        mode=mode,
        expires_at=signoff.expires_at_utc,
    )
    expected = hmac.new(key, canonical_bytes(fields), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signoff.token)


def verify_compliance(
    intent: OrderIntent,
    signoff: ComplianceSignOff,
    *,
    key: bytes,
    mode: str,
    now: datetime,
    risk_yaml_sha256: str,
) -> bool:
    if signoff.mode != mode or signoff.decision_id != intent.decision_id:
        return False
    if not _fresh(signoff.expires_at_utc, now):
        return False
    fields = signoff_fields(
        signoff_id=signoff.signoff_id,
        intent=intent,
        intent_hash=signoff.intent_sha256,
        risk_yaml_sha256=risk_yaml_sha256,
        mode=mode,
        expires_at=signoff.expires_at_utc,
    )
    expected = hmac.new(key, canonical_bytes(fields), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signoff.token)
