# Job loop

One job, one folder, one state. The state in `jobs/<id>/ticket.json` is the job. Chat memory is not.

## States

| State | Meaning | Who moves it |
| --- | --- | --- |
| `inquiry` | A message arrived. Nothing is promised. | Director opens it with `scripts/new-job.mjs`. |
| `qualifying` | Intake is filling `ticket.brief`. | Intake. |
| `brief_locked` | Every `required_brief` key is non-empty. | Script. Empty keys are rejected. |
| `proposal_sent` | Tier, price, usage, and revision cap are written, and the liaison has the proposal. | Closer, then script. |
| `awaiting_payment` | The client has the payment link or invoice text. Work has not started. | Script. |
| `in_production` | Paid, or a sample Christopher marked as a rehearsal. | Script. `--mark-paid` is a separate command. |
| `audit` | Delivery is sealed. The auditor is the only writer, and only of the audit report. | Maker seals, director moves. |
| `client_review` | Audit passed and the seal still matches. The client can see the work. | Script, after the three gates in `CLAUDE.md`. |
| `revision` | The client asked for a change inside the sold scope. This consumes one revision when production resumes. | Liaison classifies, script counts. |
| `approved` | The client accepted this delivery. | Liaison records the acceptance sentence. |
| `delivered` | Files and the delivery note are in the channel Christopher approved. | Liaison. |
| `closed` | Ledger line written. No further production. | Finance clerk. |
| `human_gate` | Christopher has to decide. `resume_state` is the only way back. | Anyone may open it. Only `--clear-human-gate` closes it, and only back to `resume_state`. |
| `killed` | No delivery. Reason is in history. | Director. |

`scripts/transition.mjs` is the only way to change `state`. Editing `ticket.json` by hand to skip a state is a failed job.

## Revision accounting

Internal audit failures return from `audit` to `in_production` and do not increment `revisions_used`.

A client revision increments the counter on the way back into `in_production`. The cap is in the niche spec. Past the cap, the script refuses another production round. Open `human_gate` and let Christopher choose a paid add-on or a stop. Do not grant a free round to be agreeable.

Scope that was not in the locked brief is a new proposal, not a revision. The liaison writes the difference in one sentence and the closer prices it.

## Folder

```
jobs/<id>/
  ticket.json
  BRIEF.md
  direction.md          art director, after brief_locked
  proposal.md           closer
  inbox/                client files, unchanged
  delivery/
    manifest.json
    seal.json
    ...exported files
  audit-report.md
  client-note.md
```

`delivery/manifest.json` lists every exported file:

```json
{ "files": [{ "path": "01-feed.png", "role": "feed-portrait" }] }
```

Roles and counts come from `niches/<niche>/spec.json` for `ticket.tier`. The checker fails if a count is off by one in either direction.

## Payment

`commercial.paid` stays false until:

```
node scripts/transition.mjs <id> awaiting_payment --mark-paid --note "<Christopher's confirmation>"
```

The finance clerk prepares the amount, the link from `studio.config.json`, and the note Christopher would have to say. The clerk does not run that command.

Samples use the same door. The note says the job is a rehearsal and no money moved. A sample is never sent to a real client and never used as a testimonial.

## Kill rules

Kill the job, do not "salvage" it, when:

- The request needs a real person's likeness and there is no written consent in `inbox/`.
- The request needs a trademark, a game studio's characters, or a celebrity.
- The ad copy makes a health, income, or financial claim the client has not put in writing in `inbox/`.
- The niche is not one of the five.
- The client wants the studio to post, spend, or run the ad account.

Record the reason in `--note` and move to `killed` or `human_gate` if money already moved.
