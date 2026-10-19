# DETACHED: a span ending in a number, now continued by another digit

Added under 0004. The span is the number `4.2`, at 31 to 34, with the
prefix `The reactor scram threshold is ` (31 code points, all of the text before it) and the
suffix ` sigma above baseline, measured `. The threshold became `4.25 sigma`. `4.2` occurs once in the
current paragraph, at 31 to 34.

- Prefix: the text before the occurrence is the stored prefix. It holds.
- Suffix: the text after it begins `5 sigma`. It does not hold.
- Word boundaries: in `leaf.text` the span ends between `2` and a space, a
  word boundary. In the current text it ends between `2` and `5`. Both are
  general category N (Nd), so that position is not a word boundary. Its
  start follows a space in both texts.

The end's boundary kind differs from the base span's, so the occurrence is
not a hit, and there is none: `DETACHED`. An implementation that counted
only letters as word code points would see a boundary between `2` and
`5`, match the base span's end, find a hit carried by the prefix, and
report `EDITED` on `4.2` inside `4.25`.

The paragraph's similarity to its base text is `2·202/405`
(`4·202 = 808 ≥ 405`). Every other leaf is unchanged and on the chain, so
the anchored paragraph and its edit are the only leftovers in their gap
and pair as `EDITED`, with no unmatched leaf left for §11.4's `EDITED`
rules. `span/a-span-ending-inside-a-word-that-still-does-is-edited` is the
control on the other side of the boundary rule, where the boundary kinds
match and the occurrence is a hit.

SPEC.md §11.5:

> 1. **Its ends are word boundaries exactly where the base span's are.** A
>    position in a text is a word boundary when it is the text's start or
>    end, or when the code points on its two sides are not both letters or
>    numbers (general category L or N). The occurrence's start is a word
>    boundary in the paired leaf's text if and only if the span's start is
>    one in `leaf.text`, and the same for its end.

SPEC.md §11.5:

> With no hit the anchor is
> `DETACHED`

SPEC.md §11.6:

> | `DETACHED` | the leaf has a pair, and the span does not survive in it | on the paired leaf, flagged, with the text as it stood at `base` |
