# DETACHED: a short suffix away from the leaf's end, and the prefix edited

The span `scram the reactor.` closes the paragraph, so its stored `suffix`
is empty, and its prefix is the full `wo channels voting to trip will `.
The current paragraph changed `will` to `shall` and gained a sentence,
` See the annex.`, after the span, which occurs once, at 183 to 201.

- Prefix: the text before the occurrence ends with `voting to trip shall `,
  not with `wo channels voting to trip will `. It does not hold.
- Suffix: shorter than 32 code points, so it must be all of the text after
  the occurrence. That text is ` See the annex.`, so the empty suffix does
  not hold.

There is no hit. An implementation that let an empty suffix match anywhere
would report `EDITED`. `context/a-short-suffix-may-end-at-the-leaf-end` is
the control, where the empty suffix does end at the leaf's end.

**What 0004 changed.** Under 0003 the case only appended the sentence and
detached, because a hit needed both sides. Under 0004 the intact prefix
carries that edit (`context/a-short-suffix-away-from-the-leaf-end-is-carried-by-the-prefix`,
`EDITED`), so this case now edits the prefix too.

The paragraph's similarity to its base text is `2·200/420`
(`4·200 = 800 ≥ 420`). Every other leaf is unchanged and on the chain, so the anchored
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
