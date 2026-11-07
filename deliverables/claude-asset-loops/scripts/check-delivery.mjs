import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { imageSize, jobDir, loadSpec, loadTicket, probeVideo } from "./lib.mjs";

const jobId = process.argv[2];
if (!jobId) {
  console.error("Usage: node scripts/check-delivery.mjs <job-id>");
  process.exit(1);
}

const ticket = loadTicket(jobId);
const spec = loadSpec(ticket.niche);
const manifestPath = join(jobDir(jobId), "delivery", "manifest.json");
const report = { job: jobId, niche: ticket.niche, tier: ticket.tier, defects: [] };

if (!ticket.tier || !spec.menu[ticket.tier]) {
  report.defects.push("ticket.tier is not a menu tier");
}
if (!existsSync(manifestPath)) {
  report.defects.push("delivery/manifest.json is missing");
  finish(report);
}

const manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
const counts = {};

for (const file of manifest.files || []) {
  const role = spec.roles[file.role];
  const path = join(jobDir(jobId), "delivery", file.path);
  if (!role) {
    report.defects.push(`${file.path}: unknown role ${file.role}`);
    continue;
  }
  if (!existsSync(path)) {
    report.defects.push(`${file.path}: missing`);
    continue;
  }
  counts[file.role] = (counts[file.role] || 0) + 1;
  if (role.kind === "image") {
    try {
      const size = imageSize(path);
      if (!role.mime.includes(size.mime)) report.defects.push(`${file.path}: mime ${size.mime}`);
      const match = role.sizes.some((item) => item.width === size.width && item.height === size.height);
      if (!match) {
        report.defects.push(`${file.path}: ${size.width}x${size.height} is outside ${file.role}`);
      }
    } catch (error) {
      report.defects.push(`${file.path}: ${error.message}`);
    }
  } else if (role.kind === "video") {
    const probe = probeVideo(path);
    if (probe.error) {
      report.defects.push(`${file.path}: video unverified (${probe.error}). Fail closed.`);
      continue;
    }
    const match = role.sizes.some((item) => item.width === probe.width && item.height === probe.height);
    if (!match) report.defects.push(`${file.path}: ${probe.width}x${probe.height} is outside ${file.role}`);
    if (!(probe.duration >= role.duration_sec.min && probe.duration <= role.duration_sec.max)) {
      report.defects.push(`${file.path}: duration ${probe.duration}s outside ${role.duration_sec.min}-${role.duration_sec.max}`);
    }
  } else if (role.kind === "file") {
    const ext = file.path.slice(file.path.lastIndexOf(".")).toLowerCase();
    if (!role.extensions.includes(ext)) report.defects.push(`${file.path}: extension ${ext}`);
  }
}

if (ticket.tier && spec.menu[ticket.tier]) {
  for (const [role, count] of Object.entries(spec.menu[ticket.tier].counts)) {
    if ((counts[role] || 0) !== count) {
      report.defects.push(`role ${role}: expected ${count}, found ${counts[role] || 0}`);
    }
  }
}

finish(report);

function finish(result) {
  console.log(JSON.stringify(result, null, 2));
  process.exit(result.defects.length ? 1 : 0);
}
