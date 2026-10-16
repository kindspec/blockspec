# EDITED: a heading that changes level only

The anchor is on the heading's first word. Its key changes from `h1` to
`h2`, so the two headings are not copies and do not pair on the chain. They
are the only leftovers in the first gap and are similar, so they pair as
`EDITED`. The text is unchanged, so the span's short prefix still starts at
the leaf's start and its short suffix still ends at its end. 0003 §8: a
heading changes level only, `EDITED`.

SPEC.md §11.2:

> A heading that changes level changes
> its key.

SPEC.md §11.3:

> 3. **Edits.** A base leaf `i` and a current leaf `j` left over in the same
>    gap pair as `EDITED` when all of these hold: their similarity is at least
>    0.5; it exceeds the similarity of `i` to every other leftover current
>    leaf in the gap by at least 0.15; and it exceeds the similarity of `j` to
>    every other leftover base leaf in the gap by at least 0.15.

SPEC.md §11.6:

> | `EDITED` | `EDITED`, and the span found | the anchor, marked changed |
