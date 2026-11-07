# Asset loop studio

A Claude Code project for one owner and a crew of agents. It sells five kinds of digital assets as paid jobs: social frames, Shopify product images, short UGC ads, YouTube packaging, and mobile-game ad creatives. Fifteen other niches are scored and left unbuilt.

Christopher owns the business. The agents run intake, pricing, production, audit, and the client note. They stop for his name, his payout, his "this invoice is paid," and the exceptions in `HUMAN.md`.

## Put it on the PC

Copy this directory to its own folder. Open that folder in Claude Code so `CLAUDE.md` belongs to the session. Run `node scripts/bootstrap.mjs` once and restart Claude Code so it loads `.claude/agents/`. Do not start from a parent repository and hope these agents win.

First message:

> Read CLAUDE.md. Run node scripts/bootstrap.mjs and node scripts/self-check.mjs. Tell me which config fields are empty and which tools are missing. Do not create a public name, do not message anyone, and do not start a sample until I answer the first blank.

## Map

| Path | Role |
| --- | --- |
| `PRESENTATION.md` | The argument, the prices, the boundary, the weak point |
| `SCORECARD.md` | Twenty niches, five built, sources on the numbers |
| `LOOP.md` | States, revisions, payment, kill rules |
| `POLICY.md` | Disclosure, likeness, IP, claims |
| `HUMAN.md` | The blanks only Christopher fills |
| `TOOLSTACK.md` | What the scripts and the render tools must do |
| `agents/` | The nine roles. `bootstrap.mjs` copies them into `.claude/agents/`, which this repository does not track |
| `niches/<id>/` | Offer, pipeline, audit, and `spec.json` |
| `scripts/` | State machine and delivery checks |

`node scripts/self-check.mjs` rehearses a temporary job: brief lock, unpaid block, pixel check, seal, revision cap. It does not call a model.

## Prices and sources

Opening prices are a menu, not a forecast. Demand figures are cited in `SCORECARD.md` from Fiverr's June 2026 Business Trends Index and Sensor Tower's State of Game Advertising 2026. Do not invent a monthly revenue number on top of them.
