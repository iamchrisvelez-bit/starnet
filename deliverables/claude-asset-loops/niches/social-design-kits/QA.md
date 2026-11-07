# Social kit audit

The checker owns pixel size and count. You own the brief.

- `offer` is readable on at least the first feed file and the last carousel slide, in the client's words.
- `proof` appears only if the brief's proof is not `none`, and it matches.
- `voice` is a judgment: the three voice words are not contradicted by slang, emoji, or a joke they did not ask for. Fail only on a clear contradiction, and quote it.
- Destinations match the roles. A TikTok-only brief does not need feed portraits unless the tier sold them. If the tier sold them, they still have to be in the delivery. The menu wins over a casual destination comment.
- The same frame device and the same three colors appear on every file. One rogue palette is a fail.
- Stories keep type out of the top and bottom 10%.
- No face without a consent file. No third-party logo.
- Words match `words_on_image` or `captions.txt` matches and no type is baked.

Pass requires every row above plus a clean checker.
