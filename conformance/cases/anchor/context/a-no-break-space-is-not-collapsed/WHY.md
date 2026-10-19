# DETACHED: a space in the prefix became a no-break space

A comment on `4.2 sigma`, with the short prefix
`The reactor scram threshold is `, all of the text before it, and a
32-code-point suffix. In the current paragraph the space between `scram`
and `threshold` is U+00A0 NO-BREAK SPACE, and `over` became `across` inside
the suffix, so the suffix does not hold. The span and the code points
beside it are unchanged. On prose only runs of U+0009, U+000A, U+000D and
U+0020 are written as one space, so the no-break space stays as it is and
the prefix is not all of the text before the occurrence. Neither side
holds: `DETACHED`. A resolver that collapsed every Unicode space would hold
the prefix and report `EDITED`. `context/a-tab-in-the-prefix-is-collapsed`
is the same edit with a tab, which is collapsed.

SPEC.md §11.5:

> For `EDITED`, the span is searched **inside the paired leaf only**. A hit is
> an occurrence of `span` that meets both of these (0004, which amends 0003
> Q13):
>
> 1. **Its neighbours are unchanged.** The code point just before the
>    occurrence in the paired leaf's text compares equal to the code point
>    just before the span in `leaf.text`, and the code point just after it to
>    the one just after the span. U+0009, U+000A, U+000D and U+0020 compare
>    equal to one another; a text's start or end compares equal only to a
>    start or end; any other code point only to itself.
> 2. **Its context holds.** The prefix holds when the paired leaf's text
>    before the occurrence ends with `prefix`; when `prefix` is shorter than
>    32 code points, counted as stored, it must be all of that text (0003,
>    addendum, detail 6: a short context sits at the leaf's edge). The
>    suffix holds in the same way, after the occurrence and at the leaf's
>    end. Which sides must hold, and how they compare, depends on the types
>    of `leaf` and of the paired leaf:
>    - **either is `code` or `table`**: both sides, compared exactly, as
>      0003 Q13 decided, for a comment and a suggestion alike.
>    - **both are `p` or `h1` to `h6`**: each of the text before the occurrence, the
>      text after it, `prefix` and `suffix` is first written on its own with
>      every run of U+0009, U+000A, U+000D and U+0020 as one U+0020. **For a
>      comment**, one side must hold whose stored context is not empty; when
>      both are empty, the span is the whole leaf and both hold. **For a
>      suggestion**, both sides must hold.
