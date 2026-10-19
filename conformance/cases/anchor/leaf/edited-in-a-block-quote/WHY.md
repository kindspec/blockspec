# EDITED: a two-line paragraph inside a block quote

The quoted paragraph's text has its `> ` prefixes removed and its two lines
joined by `\n`, which falls inside the span's suffix. Its last clause
changed, away from the span, so it pairs as `EDITED` and the span is found.

SPEC.md §6.3:

> **A leaf's content is its parsed content, as CommonMark parses it, with
> container prefixes removed**

SPEC.md §11.5:

> For `EDITED`, the span is searched **inside the paired leaf only**. A hit is
> an occurrence of `span` that meets both of these (0004, which replaces
> 0003 Q13's requirement of both sides):
> [...]
> 2. **One side of its context holds.** [...] A hit needs the prefix or the suffix
>    to hold.

SPEC.md §11.6:

> | `EDITED` | `EDITED`, and the span found | the anchor, marked changed |
