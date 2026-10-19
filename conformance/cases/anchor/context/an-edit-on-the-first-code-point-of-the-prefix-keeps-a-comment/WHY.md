# EDITED: a comment with an edit on the first code point of its prefix

As `context/an-edit-one-code-point-outside-the-prefix-is-edited`, but the
changed code point (`s` to `S`) is the first of the 32-code-point
prefix, so the prefix does not hold. The 32-code-point suffix does, and
the span still has a space on each side. For a comment on a paragraph one
side that holds and is not empty is enough: one hit, `EDITED`, at the same
offsets.

This case was `context/an-edit-on-the-first-code-point-of-the-prefix-detaches`,
which expected `DETACHED` under 0003's rule that both sides hold; 0004
changed the outcome and the case was renamed for it. The prefix's edge is
still pinned for what needs both sides:
`context/an-edit-on-the-first-code-point-of-the-prefix-detaches-a-suggestion`
for a suggestion, and
`context/edits-on-the-outer-code-points-of-both-sides-detach-a-comment` for
a comment whose suffix is edited too.

SPEC.md §11.1:

> | `span`, `prefix`, `suffix` | a W3C TextQuoteSelector inside `leaf.text`. `prefix` is the 32 code points before `span`, and `suffix` the 32 after it, or fewer where the leaf's edge is nearer. Neither crosses the leaf's edge |

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
