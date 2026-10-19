# EDITED: an edit inside one side of the stored context

`over` became `across` inside the span's 32-code-point suffix, so the
suffix does not hold. The paragraph still pairs as `EDITED`. The short
prefix, `The reactor scram threshold is `, is still all of the text before
the one occurrence, and the span still has a space on each side, so for a
comment on a paragraph the occurrence is a hit: `EDITED`, at the same
offsets.

This case was `status/detached-when-the-context-is-edited`, which expected
`DETACHED` under 0003 §8 and Q13 (the anchored leaf edited inside the
context, not the span). 0004 amends Q13 for comments on prose, so the
outcome changed and the case was renamed for it.
`status/detached-when-both-sides-of-the-context-are-edited` edits both
sides and detaches, and `suggestion/stale-with-one-side-of-its-context` is
this edit under a suggestion.

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

SPEC.md §11.6:

> | `EDITED` | `EDITED`, and the span found | the anchor, marked changed |

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
