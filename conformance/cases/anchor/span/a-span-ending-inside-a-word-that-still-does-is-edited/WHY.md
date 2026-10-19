# EDITED: a span that ended inside a word still ends inside one

Added under 0004, the control for
`span/a-span-now-ending-inside-a-longer-word-detaches`, with the same edit
(`sigma` to `sigmas`). Here the span is `4.2 sig`, 31 to 38, ending inside
`sigma`: its prefix is `The reactor scram threshold is ` (31 code points,
all of the text before it) and its suffix
`ma above baseline, measured over`.

- Prefix: holds; the text before the occurrence at 31 is the stored prefix.
- Suffix: the text after it begins `mas above baseline`. It does not hold.
- Word boundaries: in `leaf.text` the span ends between `g` and `m`, not a
  word boundary; in the current text it ends between `g` and `m` too. Its
  start follows a space in both. The kinds match at both ends.

So the occurrence is the one hit: the rule asks for boundaries exactly
where the base span has them, not for boundaries at every end. An
implementation that required a word boundary at each end of a hit would
report `DETACHED`. The alignment pairs `4.2 sig` with itself.

The paragraph's similarity to its base text is `2·202/405`
(`4·202 = 808 ≥ 405`). Every other leaf is unchanged and on the chain, so the anchored
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

SPEC.md §11.6:

> | `EDITED` | `EDITED`, and the span found | the anchor, marked changed |
