import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));

export const STUDIO_ROOT = resolve(process.env.STUDIO_ROOT || join(HERE, ".."));

export const STATES = [
  "inquiry",
  "qualifying",
  "brief_locked",
  "proposal_sent",
  "awaiting_payment",
  "in_production",
  "audit",
  "client_review",
  "revision",
  "approved",
  "delivered",
  "closed",
  "human_gate",
  "killed",
];

const FORWARD = {
  inquiry: ["qualifying", "human_gate", "killed"],
  qualifying: ["brief_locked", "human_gate", "killed"],
  brief_locked: ["proposal_sent", "human_gate", "killed"],
  proposal_sent: ["awaiting_payment", "qualifying", "human_gate", "killed"],
  awaiting_payment: ["in_production", "human_gate", "killed"],
  in_production: ["audit", "human_gate", "killed"],
  audit: ["in_production", "client_review", "human_gate", "killed"],
  client_review: ["revision", "approved", "human_gate", "killed"],
  revision: ["in_production", "human_gate", "killed"],
  approved: ["delivered", "human_gate", "killed"],
  delivered: ["closed", "human_gate"],
  closed: [],
  human_gate: [],
  killed: [],
};

export function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

export function studioPath(...parts) {
  return join(STUDIO_ROOT, ...parts);
}

export function jobDir(jobId) {
  if (!/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,80}$/.test(jobId)) {
    throw new Error(`Invalid job id: ${jobId}`);
  }
  return studioPath("jobs", jobId);
}

export function loadTicket(jobId) {
  return readJson(join(jobDir(jobId), "ticket.json"));
}

export function loadSpec(niche) {
  if (!/^[a-z0-9][a-z0-9-]{0,60}$/.test(niche)) {
    throw new Error(`Invalid niche id: ${niche}`);
  }
  const path = studioPath("niches", niche, "spec.json");
  if (!existsSync(path)) throw new Error(`Unknown niche: ${niche}`);
  return readJson(path);
}

export function canTransition(from, to) {
  return (FORWARD[from] || []).includes(to);
}

export function resumeState(ticket) {
  return ticket.resume_state || null;
}

export function listDeliveryFiles(dir) {
  if (!existsSync(dir)) return [];
  const out = [];
  const walk = (current) => {
    for (const name of readdirSync(current)) {
      if (name === "manifest.json" || name === "seal.json") continue;
      const path = join(current, name);
      const st = statSync(path);
      if (st.isDirectory()) walk(path);
      else out.push(path);
    }
  };
  walk(dir);
  return out.sort();
}

export function sha256File(path) {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

export function imageSize(path) {
  const buf = readFileSync(path);
  if (buf.length >= 24 && buf[0] === 0x89 && buf.toString("ascii", 1, 4) === "PNG") {
    return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20), mime: "image/png" };
  }
  if (buf.length >= 4 && buf[0] === 0xff && buf[1] === 0xd8) {
    const size = jpegSize(buf);
    if (!size) throw new Error(`JPEG size unreadable: ${path}`);
    return { ...size, mime: "image/jpeg" };
  }
  if (buf.length >= 12 && buf.toString("ascii", 0, 4) === "RIFF" && buf.toString("ascii", 8, 12) === "WEBP") {
    const size = webpSize(buf);
    if (!size) throw new Error(`WEBP size unreadable: ${path}`);
    return { ...size, mime: "image/webp" };
  }
  throw new Error(`Unsupported image: ${path}`);
}

function jpegSize(buf) {
  let offset = 2;
  while (offset < buf.length - 8) {
    if (buf[offset] !== 0xff) {
      offset += 1;
      continue;
    }
    const marker = buf[offset + 1];
    if (marker === 0xd8 || marker === 0xd9) {
      offset += 2;
      continue;
    }
    const length = buf.readUInt16BE(offset + 2);
    if (marker >= 0xc0 && marker <= 0xcf && marker !== 0xc4 && marker !== 0xc8 && marker !== 0xcc) {
      return { height: buf.readUInt16BE(offset + 5), width: buf.readUInt16BE(offset + 7) };
    }
    offset += 2 + length;
  }
  return null;
}

function webpSize(buf) {
  const format = buf.toString("ascii", 12, 16);
  if (format === "VP8X" && buf.length >= 30) {
    const width = 1 + buf.readUIntLE(24, 3);
    const height = 1 + buf.readUIntLE(27, 3);
    return { width, height };
  }
  if (format === "VP8 " && buf.length >= 30) {
    return { width: buf.readUInt16LE(26) & 0x3fff, height: buf.readUInt16LE(28) & 0x3fff };
  }
  if (format === "VP8L" && buf.length >= 25) {
    const bits = buf.readUInt32LE(21);
    return { width: (bits & 0x3fff) + 1, height: ((bits >> 14) & 0x3fff) + 1 };
  }
  return null;
}

export function probeVideo(path) {
  try {
    const raw = execFileSync(
      "ffprobe",
      ["-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,duration", "-of", "json", path],
      { encoding: "utf8" },
    );
    const data = JSON.parse(raw);
    const stream = data.streams && data.streams[0];
    if (!stream) return { error: "no video stream" };
    return {
      width: Number(stream.width),
      height: Number(stream.height),
      duration: Number(stream.duration),
    };
  } catch (error) {
    return { error: error.code === "ENOENT" ? "ffprobe-missing" : "ffprobe-failed" };
  }
}

export function which(cmd) {
  try {
    execFileSync("which", [cmd], { stdio: "ignore" });
    return true;
  } catch {
    return false;
  }
}

export function rel(path) {
  return relative(STUDIO_ROOT, path);
}
