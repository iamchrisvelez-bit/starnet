# YouTube packaging production

1. One system for the batch: the same type weight, the same corner for the words, the same outline color. Thumbnails in a batch should look like one channel.
2. Each plate has one subject and one text block. The subject is the video topic, drawn large enough to survive a 320×180 sidebar.
3. Words are the brief's words. Three words is the design limit. A longer approved line uses a second line, not a smaller font. Minimum cap height is 80 pixels on the 720-tall frame.
4. Set type in SVG. Model-painted letters fail audit.
5. Banner: the channel promise sits in the center safe area YouTube does not crop on television. Keep critical type inside the middle 1546×423 of the 2560×1440 file. Avatar is a simple mark that reads at 40 pixels. No tiny wordmark.
6. If `face_policy` is a supplied file, composite that file. Do not generate a new face "in their likeness."
7. Export JPEG quality 90 or PNG. Role names `thumbnail`, `banner`, `avatar`.
8. Also export a contact sheet at 320×180 per thumbnail into `delivery/preview/` and list those files in the manifest only if you add a role. Do not add them to the manifest. Put the contact sheet path in the audit notes by writing it outside `delivery/` at `jobs/<id>/preview-small/`. The checker counts every manifested file.

Checker, seal, audit.
