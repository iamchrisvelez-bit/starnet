# Tool contract

Claude Code may install tools and add scripts under `scripts/` when a contract below is unmet. New scripts stay dependency-free unless Christopher approves a package. They print a JSON result or a one-line error and exit non-zero on failure.

## Already in this folder

| Script | Contract |
| --- | --- |
| `scripts/bootstrap.mjs` | Writes `studio/readiness.json` and copies `agents/` into `.claude/agents/`. Does not pretend a missing binary is present. |
| `scripts/new-job.mjs` | Creates `jobs/<id>` for a known niche. |
| `scripts/transition.mjs` | The only state changer. |
| `scripts/seal-delivery.mjs` | Hashes `delivery/` after `in_production`. |
| `scripts/verify-seal.mjs` | Fails if delivery bytes changed after the seal. |
| `scripts/check-delivery.mjs` | Fails closed on count, pixel size, mime, and, for video, ffprobe duration. |
| `scripts/self-check.mjs` | Rehearses the loop against a temporary fixture. Run it after editing scripts. |

## Render backends

The maker calls a backend through a shell command recorded in `jobs/<id>/direction.md`. v1 does not vendor a model.

Still images. One command that reads a prompt file and writes a PNG at the exact pixel size in the role. If the backend cannot lock pixel size, the maker resizes with ImageMagick using integer scaling or a crop that the art director specified. Stretching is a defect.

Video. One command that writes an H.264 MP4, yuv420p, 1080x1920, with the duration window in the niche spec. Then ffmpeg normalizes:

```
ffmpeg -y -i input.mp4 -vf scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2 -r 30 -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 128k output.mp4
```

Padding color is part of the direction sheet. Default is black. A vertical video with letterboxing inside the frame still has to be 1080x1920 on the container.

If no video backend exists, do not accept `ugc-video-ads` or the `hooks` tier of `mobile-game-ua`. Static tiers can still run.

## Words on pictures

Model-rendered words are a defect when any letter is wrong. The maker sets type in an SVG and rasterizes it with `magick` or `rsvg-convert`, then composites onto the plate. The SVG is saved next to the export. The auditor reads the SVG text and compares it to `words_on_image`, `on_screen_words`, or `words_on_thumbnail` in the brief.

If neither rasterizer exists, ship the words as `captions.txt` in the same order as the frames and do not bake text. The proposal has to say that before payment. Changing this after payment is a human gate.

## What not to build

A web app, a client portal, a scraper of marketplace buyers, an auto-poster, or a payment integrator that charges a card. Christopher holds the payment URL. The studio hands clients that URL.
