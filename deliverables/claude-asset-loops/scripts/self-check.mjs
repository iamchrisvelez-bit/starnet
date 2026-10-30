import { spawnSync } from "node:child_process";
import { deflateSync } from "node:zlib";
import { mkdtempSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scripts = dirname(fileURLToPath(import.meta.url));
const pack = join(scripts, "..");
const root = mkdtempSync(join(tmpdir(), "asset-loop-"));
const failures = [];

const agentFiles = readdirSync(join(pack, "agents")).filter((name) => name.endsWith(".md"));
if (agentFiles.length !== 9) failures.push(`expected 9 agents, found ${agentFiles.length}`);

for (const niche of readdirSync(join(pack, "niches"))) {
  const spec = JSON.parse(readFileSync(join(pack, "niches", niche, "spec.json"), "utf8"));
  if (spec.id !== niche) failures.push(`${niche}: spec id is ${spec.id}`);
  for (const [tier, offer] of Object.entries(spec.menu)) {
    if (!Number.isFinite(offer.price_usd) || offer.price_usd <= 0) failures.push(`${niche} ${tier}: bad price`);
    for (const role of Object.keys(offer.counts)) {
      if (!spec.roles[role]) failures.push(`${niche} ${tier}: unknown role ${role}`);
    }
  }
}

function run(script, args) {
  return spawnSync(process.execPath, [join(scripts, script), ...args], {
    env: { ...process.env, STUDIO_ROOT: root },
    encoding: "utf8",
  });
}

function expect(label, result, code) {
  if (result.status !== code) {
    failures.push(`${label}: expected exit ${code}, got ${result.status}\n${result.stdout}\n${result.stderr}`);
  }
}

function png(width, height) {
  const raw = Buffer.alloc((width * 4 + 1) * height);
  for (let y = 0; y < height; y += 1) raw[y * (width * 4 + 1)] = 0;
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8;
  ihdr[9] = 6;
  const chunk = (type, data) => {
    const length = Buffer.alloc(4);
    length.writeUInt32BE(data.length);
    const body = Buffer.concat([Buffer.from(type), data]);
    let c = ~0;
    for (const byte of body) {
      c ^= byte;
      for (let i = 0; i < 8; i += 1) c = (c >>> 1) ^ (0xedb88320 & -(c & 1));
    }
    const crc = Buffer.alloc(4);
    crc.writeUInt32BE(~c >>> 0);
    return Buffer.concat([length, body, crc]);
  };
  return Buffer.concat([
    Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]),
    chunk("IHDR", ihdr),
    chunk("IDAT", deflateSync(raw)),
    chunk("IEND", Buffer.alloc(0)),
  ]);
}

mkdirSync(join(root, "niches", "fixture"), { recursive: true });
writeFileSync(
  join(root, "niches", "fixture", "spec.json"),
  JSON.stringify({
    id: "fixture",
    required_brief: ["subject"],
    commercial: { revision_cap: 1, default_usage: "test" },
    menu: { starter: { price_usd: 100, counts: { plate: 1 } } },
    roles: { plate: { kind: "image", mime: ["image/png"], sizes: [{ width: 32, height: 16 }] } },
  }),
);

expect("bootstrap", run("bootstrap.mjs", []), 0);
const created = run("new-job.mjs", ["--niche", "fixture", "--sample"]);
expect("new-job", created, 0);
const id = created.stdout.trim();
const ticketPath = join(root, "jobs", id, "ticket.json");

expect("brief blocks", run("transition.mjs", [id, "qualifying"]), 0);
expect("brief still blocked", run("transition.mjs", [id, "brief_locked"]), 1);

const ticket = JSON.parse(readFileSync(ticketPath, "utf8"));
ticket.brief.subject = "a blue square";
ticket.state = "qualifying";
writeFileSync(ticketPath, JSON.stringify(ticket));
expect("brief locks", run("transition.mjs", [id, "brief_locked"]), 0);

ticket.tier = "starter";
ticket.state = "brief_locked";
writeFileSync(ticketPath, JSON.stringify({ ...JSON.parse(readFileSync(ticketPath, "utf8")), tier: "starter" }));
expect("proposal", run("transition.mjs", [id, "proposal_sent"]), 0);
expect("awaiting", run("transition.mjs", [id, "awaiting_payment"]), 0);
expect("unpaid production", run("transition.mjs", [id, "in_production"]), 1);
expect("paid", run("transition.mjs", [id, "awaiting_payment", "--mark-paid", "--note", "sample, no money"]), 0);
expect("production", run("transition.mjs", [id, "in_production"]), 0);

const delivery = join(root, "jobs", id, "delivery");
writeFileSync(join(delivery, "plate.png"), png(8, 8));
writeFileSync(join(delivery, "manifest.json"), JSON.stringify({ files: [{ path: "plate.png", role: "plate" }] }));
expect("wrong size", run("check-delivery.mjs", [id]), 1);
expect("seal wrong", run("seal-delivery.mjs", [id]), 0);
writeFileSync(join(delivery, "plate.png"), png(32, 16));
expect("seal catches edit", run("verify-seal.mjs", [id]), 1);
expect("reseal", run("seal-delivery.mjs", [id]), 0);
expect("right size", run("check-delivery.mjs", [id]), 0);
expect("seal holds", run("verify-seal.mjs", [id]), 0);

expect("to audit", run("transition.mjs", [id, "audit"]), 0);
expect("skip client", run("transition.mjs", [id, "approved"]), 1);
expect("client", run("transition.mjs", [id, "client_review"]), 0);
expect("revision", run("transition.mjs", [id, "revision"]), 0);
expect("revision production", run("transition.mjs", [id, "in_production"]), 0);
expect("back to client", run("transition.mjs", [id, "audit"]), 0);
expect("client again", run("transition.mjs", [id, "client_review"]), 0);
expect("revision again", run("transition.mjs", [id, "revision"]), 0);
expect("cap", run("transition.mjs", [id, "in_production"]), 1);

if (failures.length) {
  console.error(failures.join("\n\n"));
  process.exit(1);
}
console.log(`self-check passed (${id})`);
