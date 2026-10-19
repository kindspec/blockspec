# EDITED: a full suffix that whitespace collapsing would shorten

The suffix side of `context/a-short-context-is-counted-as-stored`. The span
`4.2 sigma` has a 32-code-point suffix, `  above  the  baseline,  measure`,
holding four runs of two spaces, so written with each run as one space it
is 28 code points. The paragraph continues after it. `scram` became `trip`
inside the short prefix, so the prefix does not hold. Counted as stored,
the suffix is 32 code points, so it holds when the text after the
occurrence starts with it, after both are collapsed, which it does: one
side holds, the neighbours are unchanged, one hit, `EDITED`. A resolver
that measured the suffix after collapsing it would require it to be all of
the text after the occurrence, and detach the comment.

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
