# DETACHED: an edit on the first code point of a full prefix, and the suffix edited

The span `30-second window` (code points 81 to 97) has a full
32-code-point prefix, `seline, measured over a rolling `, and a full
suffix, ` by each of the three independen`. The current paragraph changes
the prefix's first code point (`s` to `S`, in `baSeline`) and, inside the
suffix, `three` to `four`. The one occurrence of the span is at 81 to 97.

- Prefix: the text before it ends with `eline, measured over a rolling `
  preceded by `S`, not `s`, so it does not end with `prefix`: the prefix's
  first code point is part of it.
- Suffix: the text after it begins ` by each of the four`, not
  ` by each of the three independen`.
- Word boundaries: unchanged at both ends (a space before, a space after).

Neither side holds, so there is no hit. `context/an-edit-one-code-point-outside-the-prefix-is-edited`
makes the same suffix edit and changes the code point just before the
prefix instead, and is `EDITED`.

**What 0004 changed.** Under 0003 this case changed only the prefix's first
code point and detached, because a hit needed both sides. Under 0004 one
side is enough, so that edit alone is now `EDITED`
(`context/an-edit-on-the-first-code-point-of-the-prefix-is-carried-by-the-suffix`).
To keep pinning that the prefix is the full 32 code points, the suffix is
now edited too: an implementation that compared a shorter prefix would
find the prefix intact and report `EDITED`.

The paragraph's similarity to its base text is `2·197/403`, at least 0.5
(`4·197 = 788 ≥ 403`). Every other leaf is unchanged and on the chain, so the anchored
paragraph and its edit are the only leftovers in their gap; they pair as
`EDITED` once their similarity is at least 0.5, and no unmatched leaf is
left for §11.4's `EDITED` rules.

SPEC.md §11.1:

> | `span`, `prefix`, `suffix` | a W3C TextQuoteSelector inside `leaf.text`. `prefix` is the 32 code points before `span`, and `suffix` the 32 after it, or fewer where the leaf's edge is nearer. Neither crosses the leaf's edge |

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
