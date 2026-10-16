# EDITED: an edit 33 code points before the span

The span `30-second window` has a full 32-code-point prefix,
`seline, measured over a rolling `. The current paragraph changes the code point just before
that prefix (`a` to `A`), so the prefix is intact and the
span is found. `context/an-edit-on-the-first-code-point-of-the-prefix-detaches`
changes the next code point instead.

SPEC.md §11.1:

> | `span`, `prefix`, `suffix` | a W3C TextQuoteSelector inside `leaf.text`. `prefix` is the 32 code points before `span`, and `suffix` the 32 after it, or fewer where the leaf's edge is nearer. Neither crosses the leaf's edge |

SPEC.md §11.5:

> For `EDITED`, the span is searched **inside the paired leaf only**. A hit is
> an occurrence of `span` with `prefix` ending where it starts and `suffix`
> starting where it ends.
