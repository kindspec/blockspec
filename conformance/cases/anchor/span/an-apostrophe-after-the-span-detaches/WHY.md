# DETACHED: `can` became `can't`

A comment on `can`, now "can't". The paragraph pairs as `EDITED`, and the
one occurrence of `can` has its short prefix, `Operators `, as all of the
text before it. The code point after it is now `'`, where it was a space,
so it is not a hit.

SPEC.md §11.5:

> 1. **Its neighbours are unchanged.** The code point just before the
>    occurrence in the paired leaf's text compares equal to the code point
>    just before the span in `leaf.text`, and the code point just after it to
>    the one just after the span. U+0009, U+000A, U+000D and U+0020 compare
>    equal to one another; a text's start or end compares equal only to a
>    start or end; any other code point only to itself.

0004, *Why each*:

> had changed (the same file). One side of the context ties the span to
> its place in the leaf; the neighbour rule keeps it from running into a
> longer token (`4` in `4.5`, `can` in `can't`, `kube` in `kube-proxy`); and
> a side whose stored context is empty does not count, so a span at the
> leaf's start still needs its suffix. A suggestion writes into the document,
> so it keeps 0003's stricter test.
