import { writeFileSync } from "node:fs";
import { join } from "node:path";
import { canTransition, jobDir, loadSpec, loadTicket, resumeState } from "./lib.mjs";

function arg(name) {
  const index = process.argv.indexOf(name);
  if (index === -1) return "";
  return process.argv[index + 1] || "";
}

const jobId = process.argv[2];
const to = process.argv[3];
const note = arg("--note");
const markPaid = process.argv.includes("--mark-paid");
const clearGate = process.argv.includes("--clear-human-gate");

if (!jobId || !to) {
  console.error("Usage: node scripts/transition.mjs <job-id> <state> [--mark-paid] [--clear-human-gate] [--note text]");
  process.exit(1);
}

const ticket = loadTicket(jobId);
const spec = loadSpec(ticket.niche);
let from = ticket.state;

if (markPaid) {
  if (from !== "awaiting_payment" || to !== "awaiting_payment") {
    console.error("--mark-paid is only valid as: transition <id> awaiting_payment --mark-paid --note confirmation");
    process.exit(1);
  }
  if (!note) {
    console.error("--mark-paid requires --note with the operator's payment confirmation");
    process.exit(1);
  }
  ticket.commercial.paid = true;
  ticket.commercial.paid_confirmed_at = new Date().toISOString();
  ticket.history.push({ at: new Date().toISOString(), from, to, note });
  writeFileSync(join(jobDir(jobId), "ticket.json"), JSON.stringify(ticket, null, 2) + "\n");
  console.log("payment recorded");
  process.exit(0);
}

if (from === "human_gate") {
  if (!clearGate) {
    console.error("human_gate stays closed until the operator passes --clear-human-gate");
    process.exit(1);
  }
  if (!resumeState(ticket)) {
    console.error("ticket.resume_state is empty; refusing to guess the return state");
    process.exit(1);
  }
  if (to !== ticket.resume_state) {
    console.error(`human_gate returns only to ${ticket.resume_state}`);
    process.exit(1);
  }
} else if (!canTransition(from, to)) {
  console.error(`Illegal transition ${from} -> ${to}`);
  process.exit(1);
}

if (to === "brief_locked") {
  const missing = (spec.required_brief || []).filter((key) => !ticket.brief[key]);
  if (missing.length) {
    console.error(`Brief missing: ${missing.join(", ")}`);
    process.exit(1);
  }
}

if (to === "proposal_sent") {
  if (!ticket.tier || !spec.menu[ticket.tier]) {
    console.error("Set ticket.tier to a menu key before proposal_sent");
    process.exit(1);
  }
  const menuPrice = spec.menu[ticket.tier].price_usd;
  if (ticket.commercial.price_usd == null) ticket.commercial.price_usd = menuPrice;
  ticket.commercial.menu_price_usd = menuPrice;
  const price = Number(ticket.commercial.price_usd);
  if (!Number.isFinite(price) || price <= 0) {
    console.error("price_usd must be a positive number");
    process.exit(1);
  }
  if (price < menuPrice * 0.8) {
    console.error("Price is more than 20% under the menu. Transition to human_gate with the reason. Do not send the proposal.");
    process.exit(1);
  }
}

if (to === "in_production") {
  if (!ticket.commercial.paid) {
    console.error("in_production requires commercial.paid. The operator sets that with --mark-paid while awaiting_payment.");
    process.exit(1);
  }
  if (from === "revision") {
    ticket.commercial.revisions_used += 1;
    if (ticket.commercial.revisions_used > ticket.commercial.revision_cap) {
      console.error("Revision cap exhausted. Open human_gate instead of another production round.");
      process.exit(1);
    }
  }
}

if (to === "human_gate" && from !== "human_gate") {
  ticket.resume_state = from;
  ticket.human_gates.push({ at: new Date().toISOString(), from, note: note || "unspecified" });
}

if (clearGate) ticket.resume_state = null;

ticket.state = to;
ticket.history.push({ at: new Date().toISOString(), from, to, note });
writeFileSync(join(jobDir(jobId), "ticket.json"), JSON.stringify(ticket, null, 2) + "\n");
console.log(`${from} -> ${to}`);
