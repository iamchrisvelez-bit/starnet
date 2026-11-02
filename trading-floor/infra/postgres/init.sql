-- Append-only journal. Apps use a role granted INSERT and SELECT only.
-- This bootstrap file does not set a password.

CREATE TABLE IF NOT EXISTS journal_events (
    journal_id UUID PRIMARY KEY,
    decision_id UUID,
    parent_decision_id UUID,
    ts_utc TIMESTAMPTZ NOT NULL,
    mode TEXT NOT NULL CHECK (mode IN ('PAPER', 'LIVE')),
    kind TEXT NOT NULL,
    actor TEXT NOT NULL,
    schema_version INTEGER NOT NULL,
    payload JSONB NOT NULL,
    prev_hash TEXT NOT NULL,
    hash TEXT NOT NULL
);

REVOKE UPDATE, DELETE ON journal_events FROM PUBLIC;
