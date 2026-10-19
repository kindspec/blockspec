# DETACHED, stale: a suggestion with an edit on the first code point of its prefix

As `context/an-edit-on-the-first-code-point-of-the-prefix-keeps-a-comment`,
for a suggestion. The changed code point (`s` to `S`) is the first of the
32-code-point prefix, so the prefix does not hold, even with whitespace
runs written as one space. A suggestion needs both sides, so the one
occurrence is not a hit: `DETACHED`, and the suggestion is stale.
`context/an-edit-one-code-point-outside-the-prefix-applies-a-suggestion`
changes the code point before it instead.

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

SPEC.md §11.7:

> **A suggestion applies only when its record's `status` is `open` and its
> anchor is `RESOLVED` or `EDITED`** (0003 Q2, Q10). Otherwise it is stale. A
> suggestion is never applied on `MOVED`. An accepted or rejected suggestion
> renders as history, never as an edit that can be applied.
