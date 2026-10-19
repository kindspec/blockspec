# EDITED: the prefix broken on its first code point, the suffix intact

Added under 0004, with the input
`context/an-edit-on-the-first-code-point-of-the-prefix-detaches` had
under 0003. The span `30-second window` (81 to 97) has the full prefix
`seline, measured over a rolling ` and the full suffix
` by each of the three independen`. The current paragraph changes only the
prefix's first code point, `s` to `S` in `baSeline`.

- Prefix: does not hold; the text before the occurrence ends with
  `Seline, measured over a rolling `.
- Suffix: holds; the text after it begins ` by each of the three independen`.
- Word boundaries: a space on both sides, as in `base`.

The suffix holds and the boundaries match, so the occurrence is the one
hit, and the alignment pairs the unchanged span with itself. This is the
case of a suffix that holds while the prefix does not. Under 0003 it was
`DETACHED`; 0004 lists it among the outcomes it gives up: "An edit right
next to a span no longer detaches it while the other side of the context
and the word boundaries hold".

The paragraph's similarity to its base text is `2·201/404`
(`4·201 = 804 ≥ 404`). Every other leaf is unchanged and on the chain, so the anchored
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

SPEC.md §11.5:

> With one hit, the
> longest common subsequence alignment (§11.2) of the base leaf's text onto
> the paired leaf's text must pair every code point of the span with the code
> point at the same position in the hit, or the anchor is `DETACHED` (0003
> §5).

0004, *Decision*:

> - **D. A span hit needs one side of its context, with its word boundaries
>   kept.** A hit needs its prefix or its suffix, not both, each compared
>   with whitespace runs as one space; and the occurrence's start and end
>   must be word boundaries exactly where the base span's are. This replaces
>   0003 Q13's requirement of both sides.

SPEC.md §11.6:

> | `EDITED` | `EDITED`, and the span found | the anchor, marked changed |
