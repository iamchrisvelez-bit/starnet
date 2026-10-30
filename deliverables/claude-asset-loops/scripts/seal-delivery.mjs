import { writeFileSync } from "node:fs";
import { join, relative } from "node:path";
import { jobDir, listDeliveryFiles, loadTicket, sha256File } from "./lib.mjs";

const jobId = process.argv[2];
if (!jobId) {
  console.error("Usage: node scripts/seal-delivery.mjs <job-id>");
  process.exit(1);
}
const ticket = loadTicket(jobId);
if (ticket.state !== "in_production") {
  console.error(`Seal is only valid from in_production (current: ${ticket.state})`);
  process.exit(1);
}
const dir = join(jobDir(jobId), "delivery");
const files = listDeliveryFiles(dir);
if (!files.length) {
  console.error("delivery/ has no files");
  process.exit(1);
}
const seal = {
  sealed_at: new Date().toISOString(),
  files: files.map((path) => ({
    path: relative(dir, path).split("\\").join("/"),
    sha256: sha256File(path),
  })),
};
writeFileSync(join(dir, "seal.json"), JSON.stringify(seal, null, 2) + "\n");
console.log(`sealed ${seal.files.length} files`);
