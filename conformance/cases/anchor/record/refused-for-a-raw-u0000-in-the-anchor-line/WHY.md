# anchor/record/refused-for-a-raw-u0000-in-the-anchor-line

`tree/policy.md` is the one paragraph `Q`, U+0000, then
` and then the reactor scram threshold is 4.2 sigma.`. Its leaf text is `Q`, U+FFFD, and the rest
(§3). The record is a comment on `4.2 sigma`, code points [43, 52),
whose `base` is the current `policy.md`. The second code point of
`leaf.text` is 33 or more code points before the span, so it is in neither
`prefix` nor `suffix`, and the anchor line holds it once. The three cases
`anchor/record/refused-for-a-raw-u0000-in-the-anchor-line`,
`anchor/record/resolves-with-a-raw-ufffd-in-the-anchor-line` and
`anchor/record/refused-for-an-escaped-u0000-in-leaf-text` differ only in how
the anchor line writes that one code point: a raw U+0000 (byte 00), a raw
U+FFFD (bytes EF BF BD), or the six characters `\u0000`.

This case writes a raw U+0000. Expected: `REFUSED(record-inconsistent)`, leaf, span and suggestion `null`.

SPEC.md §11.1, *Consistency*:

> It is also `REFUSED(record-inconsistent)` (0003, addendum of 2026-10-20)
> when its anchor line holds a raw U+0000: the line is checked as the file
> holds it, before §3's replacement, and the canonical form spells that code
> point `\u0000`. That escape does not anchor text holding a U+0000: a leaf's
> text holds U+FFFD, written as itself, wherever the file held U+0000, so a
> `leaf.text` spelling `\u0000` names no leaf of `base`.

SPEC.md §3:

> A record's frontmatter lines (§11.1) and a referrer's pin lines (§11.9) are
> checked as the file holds them, before the replacement. That shows only in
> a record's anchor line and in a pin line, whose canonical form spells
> U+0000 `\u0000`, so a raw U+0000 there is refused.

Control: `anchor/record/resolves-with-a-raw-ufffd-in-the-anchor-line`, the same bytes with U+FFFD there.

Files read (sha256, as computed before writing):
- SPEC.md 9635b4a43bff3d7d16497e8cbfae7863d65597ac9941aa9769a634fa14537a09
- cases-README.md ccc2999df3d77cfaea2a1340475cd38fc1261bd8d63262d20dc6a1018c284289
- case-body.schema.json 9512b41c957f0acae91c2ae84e7b1948e574bc06ea600e039991605152b3dcc8
- CASE-TREE.md ae9ef062966f380ebdbcdf3223d2d1d8f9ca5e294bc199166ce3c755493e7a8d
- CommonMark 0.31.2 spec.txt, from `npm pack commonmark-spec@0.31.2`
