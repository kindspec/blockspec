# EDITED: a span holding a line break, unchanged, in an edited paragraph

The span is `4.2\nsigma`: the paragraph's line break falls inside it. The
span is unchanged; `rolling` became `sliding` further on, beyond the
32-code-point suffix, so the paragraph pairs as `EDITED`. Both sides of the
context hold and the neighbours are unchanged: one hit, `EDITED`, at the
span's offsets. Only the text before and after an occurrence, `prefix` and
`suffix` have their whitespace runs written as one space; the span is
searched as it is stored. A resolver that wrote the span's line break as a
space before searching would find `4.2 sigma` nowhere in the paired leaf
and detach the comment. `context/the-span-itself-is-not-collapsed` is the
other side: the line break in the span became a space, and the span is not
found.

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
