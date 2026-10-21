# anchor/record/resolves-with-a-raw-ufffd-in-the-anchor-line

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

This case writes a raw U+FFFD, which is that code point's canonical
form (§11.1, *Strings*: "Every other code point is written as itself, in
UTF-8"; U+FFFD is not among those written `\u`). Its `leaf.text` then equals
the base leaf's text, which holds U+FFFD (§3; §11.1: "a leaf's text holds
U+FFFD, written as itself, wherever the file held U+0000").

Expected: `RESOLVED`, leaf `[0]`, span [43, 52). `base` is the current
blob, so the leaf is `EXACT` on the chain (§11.3 step 1), no other leaf
exists, and §11.5: "For `EXACT` and `MOVED`, the span keeps its offset".
§11.6: `RESOLVED` is "`EXACT`, and the span found".

This is the accepting twin of the other two cases.

Files read (sha256, as computed before writing):
- SPEC.md 9635b4a43bff3d7d16497e8cbfae7863d65597ac9941aa9769a634fa14537a09
- cases-README.md ccc2999df3d77cfaea2a1340475cd38fc1261bd8d63262d20dc6a1018c284289
- case-body.schema.json 9512b41c957f0acae91c2ae84e7b1948e574bc06ea600e039991605152b3dcc8
- CASE-TREE.md ae9ef062966f380ebdbcdf3223d2d1d8f9ca5e294bc199166ce3c755493e7a8d
- CommonMark 0.31.2 spec.txt, from `npm pack commonmark-spec@0.31.2`
