# Trading Floor

Phase 0 foundation. The eight invariants below are copied verbatim from the architecture plan. No phase, prompt, lesson, or convenience may weaken them.

1. Paper by default. Live trading requires BOTH `TRADING_MODE=live` in `.env` AND a confirmation typed by hand in the console. Mode (`PAPER` / `LIVE`) visible on every console screen and every Telegram message.
2. AI never touches the exchange. No LLM agent receives exchange/broker credentials or can call order endpoints. Only the execution service holds keys, and it only accepts orders signed off by risk and compliance.
3. Risk and compliance are plain Python, deterministic, fully unit-tested (hypothesis property tests), and read limits only from `config/risk.yaml`. No agent, prompt, or lesson may change that file; changes come from Christopher through the console with a shown diff.
4. Untrusted text stays data. News, social posts, filings, web pages are never concatenated into instructions. Every agent returns JSON validated by a Pydantic schema; invalid output = no action.
5. Fail closed. Any error, timeout, stale data (>60s), exchange reject, exchange outage, or lost heartbeat = NO new orders. Dead-man switch cancels open orders if heartbeat missing for 2 minutes.
6. Spot only. No margin, leverage, short selling, perpetual futures, options, lending, staking, or on-chain withdrawals. API keys must be trade permission only (no withdrawal); refuse to start if the key reports withdrawal rights where the exchange exposes that. Moonit desk cannot scope a wallet key this way: signing firewall + wallet balance cap instead.
7. Restricted list in config. Ship with LVMH Moët Hennessy Louis Vuitton and Christian Dior SE securities blocked; Christopher can add names or coins.
8. Everything journaled. Every signal, debate, decision, risk check, order, and fill shares a `decision_id` in an append-only journal so any trade can be replayed end to end.

The live phrase resolved by the plan is exactly `ENABLE LIVE TRADING`, typed on a TTY of the execution process. A web control, Telegram message, env var, pipe, or Compose healthcheck cannot satisfy it. Restart comes up halted.
