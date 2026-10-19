# EDITED, applies: a suggestion whose context changed only in whitespace

The paragraph was rewrapped so that `4.2 sigma` starts a line, and a
second space was typed after `above`. The text before the occurrence ends
in a line feed where the stored prefix ends in a space, and the text after
it has two spaces where the suffix has one. With each side's whitespace
runs written as one space, both sides hold, and the line feed before the
span compares equal to the space it replaced: one hit, `EDITED`, and the
suggestion applies. Under 0003 both sides were compared exactly, and it
detached.

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

0004, *Decision*:

> - **D. On prose, a comment's span needs one side of its context and its
>   neighbours.** An `EDITED` span hit needs the code points just before and
>   after it to be unchanged (whitespace matching whitespace, a leaf's edge
>   matching an edge). On a paragraph or heading, the context compares
>   whitespace runs as one space, and a comment needs one side of it that
>   holds and is not empty; a suggestion still needs both sides, as 0003 Q13
>   said, whitespace aside. Where the leaf or its pair is a code block or a
>   table, comments and suggestions keep 0003's rule: both sides, compared
>   exactly.
