# EDITED: the anchored leaf edited away from its span

The paragraph's last clause changed, more than 32 code points after the
span's suffix. Its old and new text are the only leftovers in their gap and
are similar, so they pair as `EDITED`. The span, with its 31-code-point
prefix at the leaf's start and its 32-code-point suffix, has one hit, and
the alignment carries it there.

SPEC.md §11.3:

> 3. **Edits.** A base leaf `i` and a current leaf `j` left over in the same
>    gap pair as `EDITED` when all of these hold: their similarity is at least
>    0.5; it exceeds the similarity of `i` to every other leftover current
>    leaf in the gap by at least 0.15; and it exceeds the similarity of `j` to
>    every other leftover base leaf in the gap by at least 0.15.

SPEC.md §11.5:

> For `EDITED`, the span is searched **inside the paired leaf only**. A hit is
> an occurrence of `span` that meets both of these (0004, which replaces
> 0003 Q13's requirement of both sides):
> [...]
> 2. **One side of its context holds.** [...] A hit needs the prefix or the suffix
>    to hold.

SPEC.md §11.6:

> | `EDITED` | `EDITED`, and the span found | the anchor, marked changed |
