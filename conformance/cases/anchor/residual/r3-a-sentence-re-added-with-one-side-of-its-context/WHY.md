# R3, EDITED: the span's sentence re-added with only one side of its context

Added under 0004, for the wider form of R3 that 0004 names. As in
`residual/r3-a-sentence-rewritten-and-re-added`, the sentence holding the
span was rewritten in place (to `Trips are logged.`) and the old sentence
re-added at the paragraph's end, but the re-added copy says `its value
exceeds` where the old one said `its reading exceeds`:

    Each channel is tested once a month. Trips are logged. Two trips scram. A channel trips when its value exceeds 4.2 sigma above the rolling baseline for that channel.

The span `4.2 sigma` (78 to 87 in `base`) has the prefix
` trips when its reading exceeds ` and the suffix
` above the rolling baseline for `. It occurs once, at 111 to 120.

- Prefix: the text before ends ` trips when its value exceeds `. It does
  not hold.
- Suffix: the text after begins ` above the rolling baseline for `. It
  holds.
- Word boundaries: a space on each side, as in `base`.

So the occurrence is the one hit. The paragraph pairs as `EDITED`
(similarity `2·128/318`, `4·128 = 512 ≥ 318`; the other paragraph is
unchanged on the chain). The longest common subsequence alignment of the
base text onto the current one pairs the shared first sentence, skips
`Trips are logged. Two trips scram. ` on the current side, and carries
`A channel trips when its ... for that channel.` onto the re-added copy,
`reading` against `value` pairing only an `a`; it pairs every code point of
the span with 111 to 120. Both records land on the copy, `EDITED`, and the
suggestion applies there.

**This outcome is a documented residual, not a defect.** §11.12 lists it
among the edits no resolver that reads only `base` and the current text
can tell from a legitimate one, so the case pins the resolution the rules
give, which is silently wrong for the history described here and right
for its twin.

Under 0003 this was `DETACHED`, since the prefix fails.

0004, *The residual moves in two places*:

> - **R3** is a sentence rewritten
>   and the old sentence re-added in the same leaf with the same context,
>   and the comment follows the re-added copy. Under D the re-added copy
>   needs only one side of its context, so R3 also covers a re-add that keeps
>   one side (`residual/r3-a-sentence-re-added-with-one-side-of-its-context`).
>   The alignment of §11.5 still has to carry the old span onto the copy,
>   and the copy's ends must sit on the same word boundaries.

SPEC.md §11.12:

> Four mechanisms leave current bytes identical to those a legitimate edit
> produces, so they resolve, silently, to the wrong text (0003 §9):
>
> | | mechanism | indistinguishable from | suggestions |
> | --- | --- | --- | --- |
> | R1 | a leaf deleted, and a verbatim copy of it elsewhere | a move | not affected: stale on `MOVED` |
> | R2 | a leaf rewritten to word similarity below 0.5 (0004; by code points the rewrite may be more similar), with a verbatim copy of its old text left in its place in order | a new leaf inserted beside an unchanged one | affected |
> | R3 | inside one leaf, the span's sentence rewritten and the old sentence re-added with one side of its context or both (0004), on the same word boundaries | a sentence moved within its leaf | affected |
> | R4 | a different document at the same path, by archive-and-replace or copy-and-rewrite | an edit of the document | affected |

SPEC.md §11.5:

> For `EDITED`, the span is searched **inside the paired leaf only**. A hit is
> an occurrence of `span` that meets both of these (0004, which replaces
> 0003 Q13's requirement of both sides):
>
> 1. **Its ends are word boundaries exactly where the base span's are.** A
>    position in a text is a word boundary when it is the text's start or
>    end, or when the code points on its two sides are not both letters or
>    numbers (general category L or N). The occurrence's start is a word
>    boundary in the paired leaf's text if and only if the span's start is
>    one in `leaf.text`, and the same for its end.
> 2. **One side of its context holds.** Write each text with every run of
>    U+0009, U+000A, U+000D and U+0020 as one U+0020: the paired leaf's text
>    before the occurrence and after it, each taken on its own, and `prefix`
>    and `suffix`. The prefix holds when the text before the occurrence, so
>    written, ends with `prefix` so written; when `prefix` is shorter than
>    32 code points, counted as stored, it must be all of that text (0003,
>    addendum, detail 6: a short context sits at the leaf's edge). The suffix holds in the same way, after the
>    occurrence and at the leaf's end. A hit needs the prefix or the suffix
>    to hold.
>
> Hits are counted by start position, overlapping ones included (§11.1). With no hit the anchor is
> `DETACHED`; with more than one, `REFUSED(span-ambiguous)`.

SPEC.md §11.5:

> With one hit, the
> longest common subsequence alignment (§11.2) of the base leaf's text onto
> the paired leaf's text must pair every code point of the span with the code
> point at the same position in the hit, or the anchor is `DETACHED` (0003
> §5).
