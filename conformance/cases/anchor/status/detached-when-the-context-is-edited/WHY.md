# DETACHED: edits inside both sides of the stored context

The span `4.2 sigma` has a short prefix, `The reactor scram threshold is `
(31 code points, all of the text before it), and a full suffix,
` above baseline, measured over a`. The current paragraph changes
`threshold` to `limit` inside the prefix and `over` to `across` inside the
suffix. The span occurs once, at 27 to 36.

- Prefix: the text before it is `The reactor scram limit is `, not the
  stored prefix, so a short prefix that must be all of that text does not
  hold.
- Suffix: the text after it begins ` above baseline, measured across`,
  not ` above baseline, measured over a`.

No occurrence has either side of its context, so there is no hit, and the
paragraph, still paired as `EDITED`, is `DETACHED`. 0003 §8: the anchored
leaf edited inside the context, not the span, `DETACHED`.

**What 0004 changed.** Under 0003 the case edited the suffix only (`over`
to `across`) and detached, because a hit needed both sides. Under 0004 the
intact prefix carries that edit, so it is now `EDITED`
(`context/an-edit-inside-the-suffix-is-carried-by-the-prefix`). The prefix
is now edited too, so the status this case is named for is still the one a
context edit gives when neither side survives.

The paragraph's similarity to its base text is `2·191/402`
(`4·191 = 764 ≥ 402`). Every other leaf is unchanged and on the chain, so the anchored
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
