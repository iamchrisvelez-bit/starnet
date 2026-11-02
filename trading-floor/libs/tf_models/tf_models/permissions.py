from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PermissionReport(BaseModel):
    """Normalized key permissions. None means the venue did not expose the bit."""

    model_config = ConfigDict(extra="forbid")

    venue: str
    can_trade: bool | None
    can_withdraw: bool | None
    can_transfer: bool | None
    eligibility_ok: bool | None
    eligibility_reason: str | None = None
    raw_recognized: bool
