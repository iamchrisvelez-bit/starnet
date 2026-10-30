import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { STUDIO_ROOT, studioPath, which } from "./lib.mjs";

const checks = [
  { id: "node", ok: true, detail: process.version },
  { id: "ffprobe", ok: which("ffprobe"), detail: which("ffprobe") ? "available" : "required before any video niche can pass audit" },
  { id: "ffmpeg", ok: which("ffmpeg"), detail: which("ffmpeg") ? "available" : "required to assemble video cuts" },
  { id: "magick", ok: which("magick") || which("convert"), detail: "ImageMagick rasterizes SVG text plates" },
  { id: "rsvg-convert", ok: which("rsvg-convert"), detail: "optional SVG rasterizer" },
];

const configPath = studioPath("studio.config.json");
const readiness = {
  checked_at: new Date().toISOString(),
  studio_root: STUDIO_ROOT,
  config_present: existsSync(configPath),
  tools: checks,
  block_video_until_ffprobe: !checks.find((item) => item.id === "ffprobe").ok,
  block_text_plates_until_rasterizer: !checks.find((item) => item.id === "magick").ok && !checks.find((item) => item.id === "rsvg-convert").ok,
  next_human_file: "HUMAN.md",
};

mkdirSync(studioPath("studio"), { recursive: true });
mkdirSync(studioPath("jobs"), { recursive: true });
writeFileSync(join(studioPath("studio"), "readiness.json"), JSON.stringify(readiness, null, 2) + "\n");

const missing = checks.filter((item) => !item.ok).map((item) => item.id);
console.log(JSON.stringify({ wrote: "studio/readiness.json", missing }, null, 2));
if (!readiness.config_present) {
  console.log("studio.config.json is absent. Copy studio.config.example.json and leave unknown fields blank.");
}
