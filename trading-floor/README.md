# Trading Floor — Phase 0

Personal spot-only foundation. Paper by default. This tree stops at the Phase 0 gate. It does not start playbooks, agents, the backtester, or Moonit trading.

## What is here

- Config files, including `config/risk.yaml` and the restricted issuers.
- Public crypto ingest for Coinbase Exchange, Kraken, and Alpaca market data.
- Append-only journal hash chain and a Postgres `REVOKE UPDATE, DELETE` bootstrap.
- Redis stream rules (in-memory bus in tests; `RedisBus` for the process).
- Paper engine, permission probe, KILL, pause, and the 120-second dead-man.
- Console shell: mode badge, KILL, and PAUSE on every route. The API cannot place an order or flip the mode.
- Telegram bodies from one function that prefixes `[PAPER]` or `[LIVE]`.
- Quiet hours 23:00–07:00 America/New_York.
- Moonit connector skeleton on devnet: signing firewall, no mint or launch wrapper, no Jupiter call, no signature.

## Gate

Fixtures prove:

- The internal paper account connects and can rest an order.
- KILL cancels `tf_` orders, leaves foreign orders, and blocks new orders including stops.
- A required heartbeat missing for 120 seconds cancels our open orders. At 15 seconds, entries halt and a stop may still be sent.
- A withdrawal or transfer bit refuses startup. A payload that omits the bits refuses startup. Trade-only continues.

Alpaca, Coinbase, and Kraken order keys are not in this environment. Live trade hosts are refused by the data client. Fee rates are blank so a fill is refused instead of inventing a tier. Public books can be checked with `TF_LIVE_PUBLIC_DATA=1`.

## Run the tests

```bash
cd trading-floor
uv sync
uv run pytest
cd services/moonit_connector && npm ci && npm test
cd ../../apps/console_web && npm ci && npm test
```

## Compose

Copy `.env.example` to `.env` and set the infrastructure values. Do not commit `.env`.

`TRADING_MODE=live` does nothing by itself. After a restart the execution container runs `cancel_all_ours()` and waits. On a TTY (`docker attach`), the phrase is `ENABLE LIVE TRADING`.

## Still needs Christopher

- Exchange and broker accounts, and trade-only keys.
- A verified permission payload for each live venue. Until the venue exposes the bits, startup refuses.
- His fee tier in `config/fees.yaml`.
- `RISK_TOKEN_KEY`, `COMPLIANCE_TOKEN_KEY`, console tokens, Telegram token.
- A VPS when a later phase runs overnight. Phase 0 does not deploy one.
- A devnet wallet only if he wants the Moonit connector to move past this skeleton. Phase A in this pull request does not sign.
