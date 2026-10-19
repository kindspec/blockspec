# REFUSED(pinned-orphaned): the first refusing leaf in the pinned blob

The pinned region holds three paragraphs. The first, `The scram threshold
is ...`, was deleted, which leaves it no pair (`orphaned`). The second,
`Operators review the trip logs at the start of every shift.`, was edited
(` and every outage` added) and a short paragraph, `Check the trip logs.`,
added after it in its gap (`crowded-gap`). The first refusing leaf in the
pinned blob's document order decides.

**Pairing.** The heading and `Changes ...` are on the chain, so the gap
holds the first two paragraphs on the base side and the edit and
`Check the trip logs.` on the current side. The second paragraph's
similarity to its edit is `2·61/139`; to `Check the trip logs.` it is
`2·18/83`, and the edit's to the first paragraph `2·37/186`. Both margins
hold (`40·61·83 − 40·18·139 = 102,440 ≥ 3·139·83 = 34,611`;
`40·61·186 − 40·37·139 = 248,120 ≥ 3·139·186 = 77,562`), so the second
paragraph pairs as `EDITED`. The first pairs with nothing: its similarity
to the edit is `2·37/186` and to `Check the trip logs.` `2·17/130`, both
below 0.5.

**Word similarity.** `Check the trip logs.` has the words `p`, `Check`,
`the`, `trip`, `logs.`; the second paragraph has 12, among them `the` and
`trip` but `logs` without the full stop. So `L = 3`, `T = 17`: `2·3/17`,
at least 0.3 (`20·3 = 60 ≥ 3·17 = 51`), a rival, and the second paragraph
is refused as `crowded-gap`. Against `Changes to these limits need the
approval of the safety committee.`, `EXACT`, it shares `p` and `the`:
`2·2/17`, below 0.5, so that leaf does not refuse.

**What 0004 changed.** The added paragraph was `See the annex.`, whose
word similarity to the second paragraph is `2·2/16` (`p`, `the`), below
0.3 (`20·2 = 40 < 3·16 = 48`). Under 0004 it would no longer refuse that paragraph, leaving one
refusing leaf, so the case would not test the order of several. It now
adds a rival. The expected outcome is the same.

SPEC.md §11.9:

> 0. **The referrer.** A referrer the profile refuses is refused as a whole,
>    `REFUSED(not-in-profile)`, and its transclusions are not enumerated: a
>    refused file has no tree to find them in. A conflict-marker line
>    anywhere in it counts, in its frontmatter and in a fenced code block
>    alike, whatever readings 4 and 12 say (same addendum, item 7).
> 1. **The inputs**, checked in this order; the first that fails decides
>    (same addendum, items 2 and 3, with its precision):
>    1. the path must resolve, or `REFUSED(unresolvable-path)`;
>    2. the referrer's pins must follow the grammar above, or
>       `REFUSED(record-inconsistent)`;
>    3. the target document must exist, or `REFUSED(document-missing)`;
>    4. the current target must pass the profile, or
>       `REFUSED(not-in-profile)`;
>    5. a name that only a heading slug matches in the current target is
>       `#REF!(name)` (item 6). A marker name that is also some heading's
>       slug resolves to the marker (§8.1);
>    6. the pinned blob must be readable, or `REFUSED(base-unavailable)`;
>    7. the pinned blob must pass the profile, or `REFUSED(not-in-profile)`;
>    8. a marker must bind the name in the pinned blob, or
>       `REFUSED(record-inconsistent)`.

SPEC.md §11.9:

> Where several leaves refuse, the first in the
>    pinned blob's document order is reported.
