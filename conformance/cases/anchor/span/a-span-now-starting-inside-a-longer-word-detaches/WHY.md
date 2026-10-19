# DETACHED: the span's start now falls inside a longer word

Added under 0004. `threshold` became `subthreshold`. The span `threshold`
(18 to 27 in `base`) has the short prefix `The reactor scram ` and the
full suffix ` is 4.2 sigma above baseline, me`. It occurs once in the
current text, at 21 to 30.

- Prefix: shorter than 32 code points, so it must be all of the text
  before the occurrence, which is `The reactor scram sub`. It does not hold.
- Suffix: the text after the occurrence begins
  ` is 4.2 sigma above baseline, me`. It holds.
- Word boundaries: in `leaf.text` the span starts between a space and `t`,
  a word boundary. In the current text the occurrence starts between `b`
  and `t`, which is not one.

The suffix holds, but the start is not a word boundary where the base
span's is, so the occurrence is not a hit, and there is none. An
implementation without the boundary rule would align the span onto the
`threshold` inside `subthreshold` and report `EDITED`.

The paragraph's similarity to its base text is `2·202/407`
(`4·202 = 808 ≥ 407`). Every other leaf is unchanged and on the chain, so the anchored
paragraph and its edit are the only leftovers in their gap; they pair as
`EDITED` once their similarity is at least 0.5, and no unmatched leaf is
left for §11.4's `EDITED` rules.

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

SPEC.md §11.6:

> | `DETACHED` | the leaf has a pair, and the span does not survive in it | on the paired leaf, flagged, with the text as it stood at `base` |
