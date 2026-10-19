# DETACHED: a comment whose short prefix is no longer all of the text before it

The comment on `restart every replica` has the short prefix `Note: ` (six
code points, at the leaf's start) and the short suffix ` now.` (at its
end). `Urgent. ` was added before the prefix and `now` became `today`. The
text before the occurrence, `Urgent. Note: `, ends with the prefix, and
the span still has a space on each side, so the neighbours are unchanged.
But a prefix shorter than 32 code points, as stored, holds only when it is
all of the text before the occurrence, which it no longer is. The suffix
does not hold either, so no side holds: `DETACHED`. A resolver that held a
short prefix when the text before merely ended with it would report
`EDITED`.
`context/a-short-prefix-away-from-the-edge-gives-way-to-the-suffix` keeps
the suffix and follows.

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
