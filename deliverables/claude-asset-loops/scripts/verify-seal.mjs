import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { jobDir, listDeliveryFiles, sha256File } from "./lib.mjs";
import { relative } from "node:path";

const jobId = process.argv[2];
if (!jobId) {
  console.error("Usage: node scripts/verify-seal.mjs <job-id>");
  process.exit(1);
}
const dir = join(jobDir(jobId), "delivery");
const sealPath = join(dir, "seal.json");
if (!existsSync(sealPath)) {
  console.error("delivery/seal.json is missing");
  process.exit(1);
}
const seal = JSON.parse(readFileSync(sealPath, "utf8"));
const current = new Map(
  listDeliveryFiles(dir).map((path) => [relative(dir, path).split("\\").join("/"), sha256File(path)]),
);
const errors = [];
for (const file of seal.files) {
  if (current.get(file.path) !== file.sha256) errors.push(`changed or missing: ${file.path}`);
  current.delete(file.path);
}
for (const extra of current.keys()) errors.push(`extra file after seal: ${extra}`);
if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}
console.log("seal intact");
