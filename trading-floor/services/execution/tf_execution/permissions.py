"""Startup permission probe. Unknown is a refusal. A withdrawal bit is a refusal."""

from __future__ import annotations

from tf_models.permissions import PermissionReport


def map_permission_payload(venue: str, payload: dict | None) -> PermissionReport:
    """Recognize only an explicit boolean trio. Anything else did not expose permissions."""

    if not isinstance(payload, dict):
        return PermissionReport(
            venue=venue,
            can_trade=None,
            can_withdraw=None,
            can_transfer=None,
            eligibility_ok=None,
            raw_recognized=False,
        )
    needed = ("can_trade", "can_withdraw", "can_transfer")
    if not all(key in payload for key in needed):
        return PermissionReport(
            venue=venue,
            can_trade=None,
            can_withdraw=None,
            can_transfer=None,
            eligibility_ok=None,
            raw_recognized=False,
        )
    values = [payload[key] for key in needed]
    if not all(isinstance(value, bool) for value in values):
        return PermissionReport(
            venue=venue,
            can_trade=None,
            can_withdraw=None,
            can_transfer=None,
            eligibility_ok=None,
            raw_recognized=False,
        )
    eligibility = payload.get("eligibility_ok", True)
    reason = payload.get("eligibility_reason")
    if not isinstance(eligibility, bool):
        eligibility = None
    return PermissionReport(
        venue=venue,
        can_trade=payload["can_trade"],
        can_withdraw=payload["can_withdraw"],
        can_transfer=payload["can_transfer"],
        eligibility_ok=eligibility,
        eligibility_reason=reason if isinstance(reason, str) else None,
        raw_recognized=True,
    )


def assert_permissions(report: PermissionReport) -> None:
    venue = report.venue
    if report.can_withdraw is True or report.can_transfer is True:
        raise SystemExit(f"Refusing to start: {venue} key reports withdrawal or transfer permission.")
    if report.can_withdraw is None or report.can_transfer is None or not report.raw_recognized:
        raise SystemExit(f"Refusing to start: {venue} did not expose key permissions.")
    if report.eligibility_ok is False:
        reason = report.eligibility_reason or f"could not verify {venue} eligibility"
        raise SystemExit(reason)
    if report.eligibility_ok is None or report.can_trade is not True:
        raise SystemExit(f"could not verify {venue} eligibility")
