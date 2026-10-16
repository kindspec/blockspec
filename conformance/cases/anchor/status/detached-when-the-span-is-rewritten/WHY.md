# DETACHED: the span rewritten

`4.2 sigma` became `4.5 sigma`. The paragraph pairs as `EDITED`, and the
span no longer occurs in it.

SPEC.md §11.5:

> For `EDITED`, the span is searched **inside the paired leaf only**. A hit is
> an occurrence of `span` with `prefix` ending where it starts and `suffix`
> starting where it ends.
> [...] With no hit the anchor is
> `DETACHED`

SPEC.md §11.6:

> | `DETACHED` | the leaf has a pair, and the span does not survive in it | on the paired leaf, flagged, with the text as it stood at `base` |
