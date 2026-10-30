# A studio that sells files, not a promise of virality

Speaker notes sit under each slide. Read this once before changing a niche or adding a sixth offer.

The six sentences the deck has to carry:

The buyers who used to hire a designer for a campaign now hire for a week of files. That work stayed fragmented because every brief was a custom argument and every revision was a mood. This folder is a studio with five priced offers, a state machine, and an auditor who did not make the work. It can run from inquiry to acceptance because the deliverable is a file with a pixel size, a word list, and a revision cap. It is possible now because search demand in 2026 moved toward front-end content production, and mobile game advertisers stepped up creative testing. Christopher owns the name, the payout, and the exceptions. The agents own the loop.

## 1. The product is a closed loop

Headline: Cashflow here is a paid file that survived an audit, not a folder of prompts.

The studio sells five kinds of assets. A job enters as an inquiry, leaves as a delivery, and the states in between are in `LOOP.md`. Nothing is "mostly done." The checker either accepts the pixels or it does not. The auditor either matches the brief or sends a defect list.

Notes: If a future session wants to add a chatbot, a portal, or an auto-poster, that session is no longer this business.

## 2. Why these offers exist now

Headline: In 2026 the measurable demand is for more creative files, produced often.

Fiverr's June 2026 Business Trends Index, based on searches on that marketplace:

- Canva designers in Graphics & Design, +403%.
- AI video and animation, +278%.
- AI UGC video ads, +265%.
- YouTube automation and faceless channels, +239% in Digital Marketing.
- Instagram content in Graphics & Design, +149%.
- Logo design, +76%. Facebook ads, +70%. YouTube thumbnails, +52%.

Sensor Tower's State of Game Advertising 2026, October 2025 through September 2026: the top US mobile game advertisers roughly tripled the number of new ad creatives, and the growth was mostly low-budget video tests. A cohort of 49 large advertisers peaked near 220 new creatives in a month in Q1 2026, more than double their 2024 run rate.

Notes: Quote the source if you repeat a number. Do not add a market-size TAM. Nobody measured one for this studio.

## 3. What is being built

Headline: Five commission desks share one crew and one ledger.

| Desk | Opening price | First file the client holds |
| --- | --- | --- |
| Social design kits | $180 / $240 / $360 | A week of feed and story frames |
| Shopify creative | $240 / $480 | Packshots from their photos |
| UGC video ads | $240 / $450 | Three or six short ads |
| YouTube packaging | $80 / $150 / $160 | Thumbnails that read at a small size |
| Mobile game UA | $200 / $420 | Stills or short hooks from their game |

Prices are an opening menu in each `spec.json`. They are not a claim about what the market clears. Change them after 10 paid jobs in that niche, with the job history as the reason, through a human gate.

Notes: The Shopify rank depends on a +348% line that appears in Fiverr's LinkedIn summary and not in the article body. `SCORECARD.md` names the swap (logo systems) if Christopher rejects that source.

## 4. The other fifteen

Headline: They lost on the demand signal, on the commission test, or because they duplicate a desk already built.

Logos are next in line on Fiverr's own percentages. Steam capsules have a real price band ($300–$600 for custom work in a July 2026 listing check cited by IndieGuild) and no growth rate in this pass. Roblox UGC has third-party reports of large category volume and fails the brief-and-revision test because the buyer is a crowd. Wall art is a saturated catalog. The full cards are in `SCORECARD.md`.

Notes: Do not "just add" Roblox because the volume sounds large. The loop would be a lie.

## 5. Who does the work

Headline: Nine roles, and the maker is not the auditor.

| Agent | Standard they are written to | They never |
| --- | --- | --- |
| Studio director | Executive producer on a few hundred paid jobs | Design, audit, or soothe the client |
| Intake producer | Producer who will not start with a mushy brief | Quote a price |
| Offer closer | Package seller | Unlimited revisions, hourly drift |
| Art director | Director whose sheet can be executed in another room | Render the final, or talk to the client |
| Asset maker | Export-accurate stills | Invent a slogan |
| Motion maker | Short-form editor who protects the first two seconds | Add a hook the sheet does not have |
| Auditor | Traffic lead whose job is the brief, not the beauty | Repair a file, partial credit |
| Client liaison | Account manager who sorts notes into scope | Change the price |
| Finance clerk | Bookkeeper | Mark an invoice paid |

The auditor's test is the sold request. A striking file that answers a different brief fails. Instructions are in `agents/`. Bootstrap copies them into `.claude/agents/` for Claude Code. The first time that directory appears, restart Claude Code so it loads them.

Notes: Claude Code loads these when this folder is the project. Point at the agent by name when you delegate.

## 6. The 1% that stays human

Headline: Christopher is the legal person. The loop does not need him inside the pixels.

He sets the studio name, the email, the disclosure, the payment path, and the first profile. He says the words that mark a job paid. He sends the first deliveries. He decides refunds, likeness, trademarks, claims, deep discounts, and any job that fails audit twice.

The list is `HUMAN.md`. An empty config field is a stop, not a creative opportunity.

Notes: Do not register accounts, buy ads, or invent a founder biography during a rehearsal.

## 7. From the first message to a happy client

Headline: Happiness is a written acceptance against a locked brief, not a vibe.

1. Inquiry becomes a job folder.
2. Intake asks one question at a time until every required brief field is filled.
3. The closer picks the smallest tier that covers it and writes the proposal, the usage, and the two-round cap.
4. The job waits in `awaiting_payment`. Production is script-blocked until Christopher confirms that job id.
5. The art director writes a sheet: one idea per frame, exact words, reject conditions.
6. The maker exports to the pixel size in the spec, sets type in SVG rather than trusting painted letters, and seals a hash of the folder.
7. The checker measures counts, sizes, and video duration. Missing ffprobe fails a video job closed.
8. The auditor walks the brief line by line and writes pass or fail.
9. The liaison sends the work and asks for one consolidated note.
10. A real change list consumes a revision. A new asset is a new price. "Approved" is their sentence, then the files are delivered, then the ledger closes.

Internal audit failures do not burn a client revision. The cap is enforced by `scripts/transition.mjs`.

Notes: Walk a sample through this before a stranger sees it. `node scripts/self-check.mjs` already proves the scripts. It does not prove taste.

## 8. What the auditor is protecting

Headline: The defect list is the product's spine.

A pass needs the sold count, the client's words, the client's product or game, the policy (no unconsented face, no franchise character, no invented claim), and a seal that still matches. "Make it pop" is not a defect the maker can execute, so the auditor is not allowed to write it. The report template is the shape in `agents/auditor.md`.

Two failed audits on one job stop for Christopher. That rule exists so a stubborn miss does not loop all night on his machine.

Notes: If you feel tempted to relax a row for a sample, the sample is not ready to show.

## 9. What v1 will not sell

Headline: The boundary is the business model.

No playable ads. No Roblox uploads. No faceless channel that we script and post. No theme installs. No media buying. No fake reviews, fake customers, or borrowed portfolios. No living artist's name as a style target. No marketplace the rules of which forbid the disclosure sentence in `studio.config.json`.

Catalog products (wall art, prop packs, battle-map bundles) are a different machine: nobody writes back. They can wait.

Notes: A client who wants the excluded work gets a kill or a human gate, with the reason in the ticket. They do not get a custom exception "just this once" from an agent.

## 10. Money, stated as arithmetic

Headline: Record cost per job. Do not forecast a month.

For a paid job:

`contribution = price_usd - tool_and_model_cost - processor_fee`

`price_usd` is the menu unless a human gate changed it. Tool cost is whatever that job wrote into `make.log` and the provider bills. It is not zero by assumption. Processor fee is whatever the payment URL's provider actually charges, read from that provider, not invented here. Two client rounds are already in the price. A third round does not happen for free.

There is no monthly revenue target in this pack. After 10 paid jobs in a niche, the director can show Christopher the average price, the average recorded cost, the fail rate, and the revision rate, and he can move the menu.

Notes: The weakest number in the whole studio is any sentence that sounds like "this will make $X." Do not add one.

## 11. How the machine gets built on the PC

Headline: Scripts already gate the loop. Models are a command, not a religion.

`TOOLSTACK.md` says what ffmpeg, ffprobe, and a rasterizer are for. A still backend is whatever command Christopher has that writes a PNG at a locked size. A video backend is the same idea for an MP4, followed by the ffmpeg normalize line. If a backend is missing, that tier is closed. The studio does not switch the client to a different niche to keep the agents busy.

`node scripts/bootstrap.mjs` writes `studio/readiness.json` so the next session can see the gaps without rediscovering them.

Notes: Adding a dependency needs a human yes. The scripts in this folder use Node's standard library on purpose.

## 12. First session on Claude Code

Headline: Open this folder by itself, then stop at the first blank.

Paste this as the first message:

> Read CLAUDE.md. Run node scripts/bootstrap.mjs and node scripts/self-check.mjs. Tell me which config fields are empty and which tools are missing. Do not create a public name, do not message anyone, and do not start a sample until I answer the first blank.

Then, in later sessions: one sample per niche, auditor pass, Christopher looks, then one real profile for the first niche.

Build order when the tools allow it: social kits, Shopify creative, YouTube packaging, then the two video desks after ffmpeg is installed. That order follows stills before motion, not a claim that the later desks are worse businesses. UGC is rank 3 on demand and later on setup.

Notes: Opening the parent StarNet repository instead of this folder will not make these agents the studio. Copy the folder out if you want a clean project.

## 13. The weak slide

Headline: Search growth is not a customer, and an AI label will lose some buyers.

Nothing in the source reports says these five menus will clear. The Shopify percentage is the softest citation in the top five. Game UA volume is a large-advertiser behavior, and a small studio's test creative is not that cohort. Marketplaces can restrict AI-assisted listings after this file is written. The disclosure rule will cost jobs. That cost is accepted.

What to do when someone points at this slide: show the sample, the audit report, and the blank price history. Offer to swap Shopify for logos if they do not trust the LinkedIn line. Do not answer with a projection.

## 14. Operating cadence

Headline: Judge the studio on finished jobs, not on how many agents ran.

A finished week is some of these, and a zero is an acceptable report:

- Config blanks closed, or a named blank still open.
- Samples passed by the auditor, per niche, or a tool gap that blocks them.
- One channel live, the one Christopher posted.
- Paid jobs, with state, price, and whether the client accepted.
- Jobs killed, with the policy line.
- Tool cost recorded.

The liaison does not invent a testimonial from a sample. The finance clerk does not invent a payment.

Notes: When the ledger has 10 closes in one niche, reopen the menu price. Until then, sell the menu.
