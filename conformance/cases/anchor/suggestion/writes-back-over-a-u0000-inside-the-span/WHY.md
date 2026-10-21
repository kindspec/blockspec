# anchor/suggestion/writes-back-over-a-u0000-inside-the-span

`tree/policy.md` is the bytes `b'Trip at a\x00b now.\n'`. The record is an open suggestion
on the paragraph leaf (`leaf.type` `p`), with span
`'a\ufffdb'` at code points [8, 11) of `leaf.text`
`'Trip at a\ufffdb now.'`, and `replace` `'c'`. The U+0000 is inside the span.

Expected: `RESOLVED`, span [8, 11), and the suggestion applies,
writing `written/policy.md`, the bytes `b'Trip at c now.\n'`.

SPEC.md §11.7, *Write-back*:

> A U+FFFD that §3 gives for a U+0000 comes from that U+0000,
> so a U+0000 inside the span's raw range is replaced with the rest of it
> (steps 2 and 3), and one outside it is left as it is.

> 3. Replace the range with `replace`, written exactly as stored and never
>    normalised, except at its line breaks. [...] Nothing outside the range
>    changes.

SPEC.md §11.7:

> **A suggestion applies only when its record's `status` is `open` and its
> anchor is `RESOLVED` or `EDITED`** (0003 Q2, Q10).

The record's `base` is the blob of the current `policy.md`, so its one leaf
pairs with itself on the chain (§11.3 step 1, "Its pairs are `EXACT`"), no
other leaf exists for §11.4's `EXACT` rules to find, and the span keeps its
offset (§11.5: "For `EXACT` and `MOVED`, the span keeps its offset in the
paired leaf"). The status is `RESOLVED` (§11.6: "`EXACT`, and the span
found"). The record's `status` is `open`, so the suggestion applies.

The anchor line writes U+FFFD as itself, which is its canonical form (§11.1,
*Strings*: U+FFFD is not in the list written `\u`, and "Every other code
point is written as itself, in UTF-8"), and §11.1 says "a leaf's text holds
U+FFFD, written as itself, wherever the file held U+0000".

The span lies strictly inside the leaf, with content code points on both
sides, so `a` and `b` map to raw positions without depending on which raw
characters outside the content §11.7's list names.

SPEC.md §3:

> **U+0000 is replaced with U+FFFD**, as the pinned grammar requires
> (CommonMark 0.31.2 §2.3, "Insecure characters").

Files read (sha256, as computed before writing):
- SPEC.md 9635b4a43bff3d7d16497e8cbfae7863d65597ac9941aa9769a634fa14537a09
- cases-README.md ccc2999df3d77cfaea2a1340475cd38fc1261bd8d63262d20dc6a1018c284289
- case-body.schema.json 9512b41c957f0acae91c2ae84e7b1948e574bc06ea600e039991605152b3dcc8
- CASE-TREE.md ae9ef062966f380ebdbcdf3223d2d1d8f9ca5e294bc199166ce3c755493e7a8d
- CommonMark 0.31.2 spec.txt, from `npm pack commonmark-spec@0.31.2`
