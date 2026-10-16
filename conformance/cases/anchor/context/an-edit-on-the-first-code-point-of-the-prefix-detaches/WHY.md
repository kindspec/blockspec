# DETACHED: an edit on the first code point of a full prefix

As `context/an-edit-one-code-point-outside-the-prefix-is-edited`, but the
changed code point (`s` to `S`) is the first of the 32-code-point
prefix. No occurrence of the span has the stored prefix before it.

SPEC.md §11.1:

> | `span`, `prefix`, `suffix` | a W3C TextQuoteSelector inside `leaf.text`. `prefix` is the 32 code points before `span`, and `suffix` the 32 after it, or fewer where the leaf's edge is nearer. Neither crosses the leaf's edge |

SPEC.md §11.5:

> For `EDITED`, the span is searched **inside the paired leaf only**. A hit is
> an occurrence of `span` with `prefix` ending where it starts and `suffix`
> starting where it ends.
> [...] With no hit the anchor is
> `DETACHED`
