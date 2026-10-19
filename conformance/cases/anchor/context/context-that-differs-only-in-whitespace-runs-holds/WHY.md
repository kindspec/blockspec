# EDITED: both sides of the context changed only in whitespace

Added under 0004. The paragraph was rewrapped: the space after `over`, in
the prefix `seline, measured over a rolling `, became a line break, and
the suffix ` by each of the three independen` gained a second space after
`of`. Its text is now

    The reactor scram threshold is 4.2 sigma above baseline, measured over
    a rolling 30-second window by each of  the three independent channels, ...

with `\n` after `over` and two spaces after `of`. The span occurs once, at
81 to 97; the line break replaced one code point, so nothing before the
span moved.

- Prefix: the text before the occurrence ends `measured over\na rolling `.
  Written with each whitespace run as one space, it ends with
  `seline, measured over a rolling `, so it holds. Compared as stored, it
  would not.
- Suffix: the text after it begins ` by each of  the three independen`;
  so written, ` by each of the three independen`. It holds, and as stored
  it would not.
- Word boundaries: a space or line break on each side, as in `base`.

Both sides hold once whitespace runs are written as one space; neither
holds without that, so an implementation that compares the context as
stored reports `DETACHED`. The alignment skips the base space after `over`
for the line break and pairs the span with itself.

The paragraph's similarity to its base text is `2·201/405`
(`4·201 = 804 ≥ 405`). Every other leaf is unchanged and on the chain, so the anchored
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
