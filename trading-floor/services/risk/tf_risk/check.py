"""Risk evaluation. A failed check does not mint a sign-off."""

from __future__ import annotations

import hashlib
import hmac
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from tf_config.load import FloorConfig
from tf_models.common import decimal_str, format_ts
from tf_models.market import Quote
from tf_models.orders import OrderIntent
from tf_models.signoff import CANONICAL_FIELDS, RiskSignOff, canonical_bytes
from tf_risk.quotes import quote_is_stale
from tf_risk.quiet import quiet_hours_block_intent

CEX_TTL = timedelta(seconds=30)


def _rule(rule_id: str, passed: bool, observed: str, limit: str) -> dict:
    return {"rule_id": rule_id, "passed": passed, "observed": observed, "limit": limit}


def evaluate_risk(
    intent: OrderIntent,
    config: FloorConfig,
    *,
    now: datetime,
    quote: Quote | None,
    loaded_hash: str | None = None,
) -> dict:
    crypto = config.risk["crypto"]
    shared_hash = loaded_hash or config.risk_yaml_sha256
    rules: list[dict] = []
    max_age = int(crypto["quote_max_age_sec"])
    if quote is None:
        rules.append(_rule("quote_age", False, "missing", f"<={max_age}s"))
    else:
        stale = quote_is_stale(quote, now, max_age_sec=max_age)
        rules.append(_rule("quote_age", not stale, "stale" if stale else "fresh", f"<={max_age}s"))

    start = str(config.approvals["quiet_hours_start_et"])
    end = str(config.approvals["quiet_hours_end_et"])
    blocked = quiet_hours_block_intent(intent.intent, now, start, end)
    rules.append(_rule("quiet_hours", not blocked, intent.intent, f"entries blocked {start}-{end} ET"))

    if intent.intent == "entry":
        has_stop = intent.stop is not None and intent.stop > 0
        rules.append(
            _rule(
                "require_stop_on_entry",
                has_stop,
                "missing" if not has_stop else decimal_str(intent.stop) or "",
                "stop required",
            )
        )
        market_ok = intent.order_type != "market"
        rules.append(_rule("order_type", market_ok, intent.order_type, "limit for entry"))
    elif intent.order_type == "market":
        allowed = set(crypto["market_orders_allowed_for"])
        rules.append(_rule("order_type", intent.intent in allowed, intent.intent, ",".join(sorted(allowed))))

    rules.append(_rule("risk_yaml_hash", shared_hash == config.risk_yaml_sha256, shared_hash, config.risk_yaml_sha256))
    passed = all(rule["passed"] for rule in rules)
    return {
        "decision_id": intent.decision_id,
        "passed": passed,
        "rules": rules,
        "risk_yaml_sha256": config.risk_yaml_sha256,
        "checked_at_utc": now.astimezone(timezone.utc),
    }


def intent_sha256(intent: OrderIntent) -> str:
    body = {
        "decision_id": str(intent.decision_id),
        "venue": intent.venue,
        "symbol": intent.symbol,
        "side": intent.side,
        "order_type": intent.order_type,
        "qty": decimal_str(intent.qty),
        "limit_price": decimal_str(intent.limit_price),
        "intent": intent.intent,
        "stop": decimal_str(intent.stop),
    }
    raw = __import__("json").dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def signoff_fields(
    *,
    signoff_id: UUID,
    intent: OrderIntent,
    intent_hash: str,
    risk_yaml_sha256: str,
    mode: str,
    expires_at: datetime,
) -> dict[str, str | None]:
    fields = {
        "signoff_id": str(signoff_id),
        "decision_id": str(intent.decision_id),
        "intent_sha256": intent_hash,
        "risk_yaml_sha256": risk_yaml_sha256,
        "mode": mode,
        "venue": intent.venue,
        "symbol": intent.symbol,
        "side": intent.side,
        "qty": decimal_str(intent.qty),
        "limit_price": decimal_str(intent.limit_price),
        "intent": intent.intent,
        "expires_at": format_ts(expires_at),
    }
    if tuple(fields) != tuple(CANONICAL_FIELDS) and set(fields) != set(CANONICAL_FIELDS):
        raise RuntimeError("canonical field set drifted")
    return fields


def mint_risk_signoff(
    intent: OrderIntent,
    *,
    key: bytes,
    mode: str,
    now: datetime,
    risk_yaml_sha256: str,
    ttl: timedelta = CEX_TTL,
) -> RiskSignOff:
    signoff_id = uuid.uuid4()
    expires = now.astimezone(timezone.utc) + ttl
    digest = intent_sha256(intent)
    fields = signoff_fields(
        signoff_id=signoff_id,
        intent=intent,
        intent_hash=digest,
        risk_yaml_sha256=risk_yaml_sha256,
        mode=mode,
        expires_at=expires,
    )
    token = hmac.new(key, canonical_bytes(fields), hashlib.sha256).hexdigest()
    return RiskSignOff(
        signoff_id=signoff_id,
        decision_id=intent.decision_id,
        order_intent_id=uuid.uuid4(),
        intent_sha256=digest,
        risk_yaml_sha256=risk_yaml_sha256,
        mode=mode,  # type: ignore[arg-type]
        venue=intent.venue,
        symbol=intent.symbol,
        side=intent.side,
        qty=intent.qty,
        limit_price=intent.limit_price,
        intent=intent.intent,
        issued_at_utc=now.astimezone(timezone.utc),
        expires_at_utc=expires,
        token=token,
    )


def discard_quiet_entries(intents: list[OrderIntent], now: datetime, config: FloorConfig) -> list[OrderIntent]:
    """First line: entry proposals during quiet hours are discarded before risk."""

    start = str(config.approvals["quiet_hours_start_et"])
    end = str(config.approvals["quiet_hours_end_et"])
    kept: list[OrderIntent] = []
    for intent in intents:
        if quiet_hours_block_intent(intent.intent, now, start, end):
            continue
        kept.append(intent)
    return kept
