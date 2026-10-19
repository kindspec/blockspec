# DETACHED: a span at the leaf's start whose suffix was edited

The span `Operators` opens the paragraph, so its stored `prefix` is empty,
and `review` became `read` inside its suffix. The occurrence still opens
the paired leaf, so its neighbours are unchanged and the empty prefix is
all of the text before it. But a comment needs one side that holds **and
whose stored context is not empty**, and the suffix does not hold:
`DETACHED`. A resolver that counted the empty prefix as a side that holds
would report `EDITED`.

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

> had changed (the same file). One side of the context ties the span to
> its place in the leaf; the neighbour rule keeps it from running into a
> longer token (`4` in `4.5`, `can` in `can't`, `kube` in `kube-proxy`); and
> a side whose stored context is empty does not count, so a span at the
> leaf's start still needs its suffix. A suggestion writes into the document,
> so it keeps 0003's stricter test.
