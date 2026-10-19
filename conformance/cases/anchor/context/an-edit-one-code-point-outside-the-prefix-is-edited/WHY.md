# EDITED: an edit 33 code points before the span, and the suffix edited

The span `30-second window` has a full 32-code-point prefix,
`seline, measured over a rolling `. The current paragraph changes the
code point just before that prefix (`a` to `A`, in `bAseline`), so the
prefix is intact. It also changes `three` to `four` inside the suffix
` by each of the three independen`, so the suffix does not hold.

- Prefix: the text before the one occurrence, at 81, ends with
  `seline, measured over a rolling `. It holds.
- Suffix: the text after it begins ` by each of the four`. It does not hold.
- Word boundaries: a space on both sides of the occurrence, as in `base`.

One side holds and the boundaries match, so the occurrence is the one
hit. The longest common subsequence alignment pairs the unchanged span
with itself at 81 to 97.
`context/an-edit-on-the-first-code-point-of-the-prefix-detaches` changes
the next code point instead and detaches.

**What 0004 changed.** The outcome is the same as under 0003, but the
suffix edit is new: under 0003 the case left the suffix intact, and under
0004 an intact suffix alone would give `EDITED` whatever the prefix said,
so the case would no longer show where the prefix starts. This case is
also the one where the prefix holds and the suffix does not.

The paragraph's similarity to its base text is `2·197/403`
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

SPEC.md §11.5:

> With one hit, the
> longest common subsequence alignment (§11.2) of the base leaf's text onto
> the paired leaf's text must pair every code point of the span with the code
> point at the same position in the hit, or the anchor is `DETACHED` (0003
> §5).

SPEC.md §11.6:

> | `EDITED` | `EDITED`, and the span found | the anchor, marked changed |
