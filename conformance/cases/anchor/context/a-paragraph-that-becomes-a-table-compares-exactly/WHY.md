# DETACHED: a paragraph of pipes that became a table

The anchored leaf is a paragraph of three lines with pipes and no
delimiter row, text `Service | Limit\napi | 10\nweb | 20`. A delimiter row
was added, making it a table, and row `api` was renamed `db`; the table's
text is `Service | Limit\ndb | 10\nweb | 20`, and the two pair as
`EDITED`. The comment is on `10`. Its short suffix, `\nweb | 20`, is still
all of the text after the occurrence, but its short prefix is not. One of
the two leaves is a table, so both sides must hold, compared exactly:
`DETACHED`. A resolver that chose the rule by the anchored leaf's type
alone would treat this as prose and move the comment onto `db`'s `10`, the
hole 0004's second review found.

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

0004, *How it was reached*:

> A second review found that scope decided by the anchored leaf's type
> alone left two of these open across a change of type: a paragraph of
> pipes becoming a table with row api renamed db moved a comment onto db's
> `10`, and a paragraph of code becoming a Python block with `remove(f)`
> indented into the loop let a suggestion apply there. 0003 detached both.
> The comparison is now exact when either leaf is a code block or a table,
> and both detach.
