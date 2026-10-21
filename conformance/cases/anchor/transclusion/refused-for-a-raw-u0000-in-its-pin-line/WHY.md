# anchor/transclusion/refused-for-a-raw-u0000-in-its-pin-line

The repository holds `doc.md`, the referrer, and the target `p`, U+FFFD,
`.md` (a file name holding U+FFFD, UTF-8 bytes EF BF BD), whose bytes are
`b'<!-- #scram -->\nThe scram threshold is 4.2 sigma.\n'`: the marker `scram` binding the paragraph `[1]`. `doc.md` has
frontmatter on lines 1 to 4 holding `pins:` and one pin line whose `blob` is
the target's current blob, then on line 6 the one transclusion paragraph
`[Scram](p?.md#scram "transclude")`, where `?` is the byte(s) noted below.

Here the pin line's `path` holds a raw U+0000 (byte 00) where the twin
`anchor/transclusion/resolves-with-a-raw-ufffd-in-its-pin-line` holds a raw U+FFFD; the destination holds a raw U+FFFD in
both. Nothing else differs.

Expected: the one transclusion, `[0]`, `REFUSED(record-inconsistent)`, unit
`null`.

SPEC.md §3:

> A record's frontmatter lines (§11.1) and a referrer's pin lines (§11.9) are
> checked as the file holds them, before the replacement. That shows only in
> a record's anchor line and in a pin line, whose canonical form spells
> U+0000 `\u0000`, so a raw U+0000 there is refused.

SPEC.md §11.9:

> **Every transclusion in the
> referrer is `REFUSED(record-inconsistent)`** when the frontmatter has [...]
> a pin line not in the canonical form (one holding
> a raw U+0000 included, §3)

Step 1.1 comes first and passes: the destination's path, `p`, U+FFFD,
`.md`, is relative and names a file. Step 1.2, "the referrer's pins must
follow the grammar above, or `REFUSED(record-inconsistent)`", then decides.

Control: `anchor/transclusion/resolves-with-a-raw-ufffd-in-its-pin-line`.

Files read (sha256, as computed before writing):
- SPEC.md 9635b4a43bff3d7d16497e8cbfae7863d65597ac9941aa9769a634fa14537a09
- cases-README.md ccc2999df3d77cfaea2a1340475cd38fc1261bd8d63262d20dc6a1018c284289
- case-body.schema.json 9512b41c957f0acae91c2ae84e7b1948e574bc06ea600e039991605152b3dcc8
- CASE-TREE.md ae9ef062966f380ebdbcdf3223d2d1d8f9ca5e294bc199166ce3c755493e7a8d
- CommonMark 0.31.2 spec.txt, from `npm pack commonmark-spec@0.31.2`
