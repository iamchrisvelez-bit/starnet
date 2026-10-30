# UGC video audit

Grab frames at 0s, 2s, and the last second of each file.

- At 2 seconds the hook line is already readable. A fade-in that hides it fails.
- The three hooks are actually different lines.
- The product in frame is the product in `inbox/`.
- The call to action is the brief's call to action, present at the end.
- Proof on screen is empty unless the brief supplied it, and then it matches.
- No spoken claim that is not also in the brief.
- No real-person likeness without consent. A fictional presenter who is a lookalike fails.
- Duration and frame size come from the checker. A missing ffprobe result is a fail even if the file plays on your machine.
- Covers match their ad's hook line.
- Captions sit outside the top 12% and bottom 18%.

The ad does not have to be entertaining. It has to be the ad they bought.
