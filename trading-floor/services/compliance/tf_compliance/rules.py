from __future__ import annotations

import hashlib
import hmac
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from tf_config.load import FloorConfig
from tf_models.orders import OrderIntent
from tf_models.signoff import ComplianceSignOff
from tf_risk.check import intent_sha256, signoff_fields
from tf_models.signoff import canonical_bytes

CEX_TTL = timedelta(seconds=30)


def _rule(rule_id: str, passed: bool, observed: str, limit: str) -> dict:
    return {"rule_id": rule_id, "passed": passed, "observed": observed, "limit": limit}


def _names(config: FloorConfig) -> set[str]:
    restricted = config.restricted
    found: set[str] = set()
    for issuer in restricted.get("issuers") or []:
        if isinstance(issuer, dict) and issuer.get("name"):
            found.add(str(issuer["name"]).casefold())
    for alias in restricted.get("aliases") or []:
        found.add(str(alias).casefold())
    for coin in restricted.get("coins") or []:
        found.add(str(coin).casefold())
    return found


def is_restricted(intent: OrderIntent, config: FloorConfig) -> bool:
    blocked = _names(config)
    candidates = [intent.symbol, intent.issuer_name or ""]
    return any(candidate.casefold() in blocked for candidate in candidates if candidate)


def evaluate_compliance(intent: OrderIntent, config: FloorConfig, *, now: datetime, mode: str) -> dict:
    rules: list[dict] = []
    flags = intent.flags
    leverage_ok = flags.leverage == Decimal("1")
    rules.append(_rule("leverage", leverage_ok, str(flags.leverage), "1"))
    for name in ("margin", "short", "perpetual", "option", "lending", "staking", "withdraw"):
        active = bool(getattr(flags, name))
        rules.append(_rule(f"spot_{name}", not active, str(active), "false"))
    restricted = is_restricted(intent, config)
    rules.append(_rule("restricted", not restricted, intent.issuer_name or intent.symbol, "not listed"))
    sell_open = intent.side == "sell" and intent.position_qty <= 0 and intent.intent == "entry"
    rules.append(_rule("sell_to_open", not sell_open, intent.side, "long-only"))
    equities_on = bool(config.venues.get("equities_enabled"))
    equities_order = intent.market == "equities"
    rules.append(_rule("equities_enabled", (not equities_order) or equities_on, intent.market, "equities flag"))
    if mode == "PAPER" and intent.venue not in {"paper_engine"}:
        rules.append(_rule("paper_route", False, intent.venue, "paper_engine"))
    else:
        rules.append(_rule("paper_route", True, intent.venue, mode))
    passed = all(rule["passed"] for rule in rules)
    return {
        "decision_id": intent.decision_id,
        "passed": passed,
        "rules": rules,
        "checked_at_utc": now.astimezone(timezone.utc),
    }


def mint_compliance_signoff(
    intent: OrderIntent,
    *,
    key: bytes,
    mode: str,
    now: datetime,
    risk_yaml_sha256: str,
    ttl: timedelta = CEX_TTL,
) -> ComplianceSignOff:
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
    return ComplianceSignOff(
        signoff_id=signoff_id,
        decision_id=intent.decision_id,
        intent_sha256=digest,
        mode=mode,  # type: ignore[arg-type]
        issued_at_utc=now.astimezone(timezone.utc),
        expires_at_utc=expires,
        token=token,
    )
