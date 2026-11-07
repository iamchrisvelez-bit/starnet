import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { loadSpec, studioPath } from "./lib.mjs";

function arg(name, fallback = "") {
  const index = process.argv.indexOf(name);
  if (index === -1) return fallback;
  return process.argv[index + 1] || fallback;
}

const niche = arg("--niche");
const client = arg("--client", "");
const channel = arg("--channel", "unspecified");
const sample = process.argv.includes("--sample");

if (!niche) {
  console.error("Usage: node scripts/new-job.mjs --niche <id> [--client name] [--channel email] [--sample]");
  process.exit(1);
}

const spec = loadSpec(niche);
const stamp = new Date().toISOString().slice(0, 10);
const suffix = Math.random().toString(36).slice(2, 6);
const id = `${stamp}-${niche.slice(0, 12)}-${suffix}`;
const dir = studioPath("jobs", id);
mkdirSync(join(dir, "inbox"), { recursive: true });
mkdirSync(join(dir, "delivery"), { recursive: true });

const ticket = {
  id,
  niche,
  sample,
  state: "inquiry",
  resume_state: null,
  tier: null,
  client: { name: client, channel, handle: "" },
  brief: {},
  commercial: {
    currency: "USD",
    menu_price_usd: null,
    price_usd: null,
    discount_reason: "",
    paid: false,
    paid_confirmed_at: null,
    revision_cap: spec.commercial.revision_cap,
    revisions_used: 0,
    usage: spec.commercial.default_usage,
  },
  human_gates: [],
  history: [{ at: new Date().toISOString(), from: null, to: "inquiry", note: sample ? "sample job" : "opened" }],
};

writeFileSync(join(dir, "ticket.json"), JSON.stringify(ticket, null, 2) + "\n");
writeFileSync(
  join(dir, "BRIEF.md"),
  `# Brief\n\nStatus: empty.\n\nFill every field in niches/${niche}/OFFER.md before leaving qualifying.\nA blank required field keeps this job in qualifying.\n`,
);
console.log(id);
