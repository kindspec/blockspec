# DETACHED: the span's end now falls inside a longer word

Added under 0004. `sigma` became `sigmas`. The span `4.2 sigma` still
occurs, once, at 31 to 40, with the short prefix
`The reactor scram threshold is ` intact as all of the text before it.

- Prefix: holds.
- Suffix: the text after the occurrence begins `s above baseline`, not
  ` above baseline, measured over a`. It does not hold.
- Word boundaries: in `leaf.text` the span ends between `a` and a space,
  a word boundary. In the current text the occurrence ends between `a` and
  `s`, two letters, which is not one.

One side of the context holds, but the occurrence's end is not a word
boundary where the base span's is, so it is not a hit, and there is none.
Without the boundary rule it would be the hit, and the comment would
follow its characters into a different word: 0004 records the replay case,
a comment on `turn on [[Highlight` that followed into
`turn on [[Highlighter|`. `span/a-span-ending-inside-a-word-that-still-does-is-edited`
is the control, with the same edit and a span whose end was already
inside the word.

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

0004, *Why each*:

> The word-boundary condition is what makes
> one side safe in the case the replay found: without it, a comment on
> `turn on [[Highlight` followed its characters into
> `turn on [[Highlighter|`, a different link, once the suffix was ignored.

SPEC.md §11.6:

> | `DETACHED` | the leaf has a pair, and the span does not survive in it | on the paired leaf, flagged, with the text as it stood at `base` |
