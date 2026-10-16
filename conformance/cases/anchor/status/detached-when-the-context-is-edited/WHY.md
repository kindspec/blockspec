# DETACHED: an edit inside the stored context

`over` became `across` inside the span's 32-code-point suffix. The
paragraph still pairs as `EDITED`, but no occurrence of the span is
followed by the stored suffix, so there is no hit. 0003 §8: the anchored
leaf edited inside the context, not the span, `DETACHED`.

SPEC.md §11.5:

> For `EDITED`, the span is searched **inside the paired leaf only**. A hit is
> an occurrence of `span` with `prefix` ending where it starts and `suffix`
> starting where it ends.
> [...] With no hit the anchor is
> `DETACHED`

SPEC.md §11.6:

> | `DETACHED` | the leaf has a pair, and the span does not survive in it | on the paired leaf, flagged, with the text as it stood at `base` |
