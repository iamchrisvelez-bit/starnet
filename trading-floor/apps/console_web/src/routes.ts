export const ROUTES = [
  { path: "/floor", title: "Floor", body: "No agent stations in Phase 0. The shell is up; runners are not." },
  { path: "/approvals", title: "Approvals", body: "Inbox is empty. Phase 0 does not request trade approval." },
  { path: "/positions", title: "Positions", body: "No positions loaded. KILL does not flatten." },
  { path: "/orders", title: "Orders", body: "Orders and fills appear here when execution reports them." },
  { path: "/equity", title: "Equity", body: "Equity versus buy-and-hold BTC is a later mark." },
  { path: "/playbooks", title: "Playbooks", body: "Playbooks are not part of Phase 0." },
  { path: "/research", title: "Research", body: "Research documents are not ingested in Phase 0." },
  { path: "/chat", title: "Chat", body: "Floor Chief is not running. This screen cannot change risk limits." },
  { path: "/costs", title: "Costs", body: "No model spend in Phase 0. The daily AI cap is unset, so nothing calls a model." },
  { path: "/guards", title: "Guards", body: "Quiet hours are 23:00–07:00 America/New_York. Dead-man cancel is 120 seconds." },
  { path: "/settings", title: "Settings", body: "Risk edits are not wired in Phase 0. Restricted names ship blocked." },
] as const;
