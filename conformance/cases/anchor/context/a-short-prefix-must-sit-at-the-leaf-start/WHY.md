# DETACHED: a short prefix away from the leaf's start, and the suffix edited

The span `The reactor scram` opens the paragraph, so its stored `prefix` is
empty, and its suffix is the full ` threshold is 4.2 sigma above ba`. The
current paragraph gained `In short: ` in front and changed `threshold` to
`limit`. The span occurs once, at 10 to 27.

- Prefix: shorter than 32 code points, so it must be all of the text
  before the occurrence. That text is `In short: `, not the empty string, so
  the prefix does not hold, although every text ends with `""`.
- Suffix: the text after the occurrence begins ` limit is`, not
  ` threshold is 4.2 sigma above ba`. It does not hold.

There is no hit. An implementation that let an empty prefix match anywhere
would find a hit here and report `EDITED`.

**What 0004 changed.** Under 0003 the case only added `In short: ` and
detached, because a hit needed both sides. Under 0004 the intact suffix
carries that edit (`context/a-short-prefix-away-from-the-leaf-start-is-carried-by-the-suffix`,
`EDITED`), so this case now edits the suffix too: the short prefix's edge
rule is the only thing between it and a hit.

The paragraph's similarity to its base text is `2·194/410`
(`4·194 = 776 ≥ 410`). Every other leaf is unchanged and on the chain, so the anchored
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

0003, addendum, detail 6:

> Without the rule, a span at a leaf's start,
> stored with an empty `prefix`, could land on a later occurrence of it that
> the same `suffix` follows.

SPEC.md §11.6:

> | `DETACHED` | the leaf has a pair, and the span does not survive in it | on the paired leaf, flagged, with the text as it stood at `base` |
