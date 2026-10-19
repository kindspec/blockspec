# DETACHED: a code block that became a paragraph

The reverse of `context/a-paragraph-that-becomes-a-code-block-compares-exactly`.
The anchored leaf is a code block; its fences and indentation were removed,
leaving a paragraph, and the two pair as `EDITED`. The comment on
`remove(f)` has a 32-code-point prefix ending in four spaces of
indentation, which the paragraph's text before the occurrence does not
end with. The anchored leaf is a code block, so both sides are compared
exactly: `DETACHED`. As prose the prefix would hold.

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

0004, *Why each*:

> In code and tables, whitespace and the cells beside a span carry meaning
> that prose does not: a line's indentation is its scope in Python and its
> parent in YAML, and a table row's first cell names what the others
> describe. So those leaves keep 0003's exact, two-sided rule, whichever side
> of the edit they are on: a paragraph of pipes that becomes a table, or of
> code that becomes a code block, is compared exactly too. The replay
