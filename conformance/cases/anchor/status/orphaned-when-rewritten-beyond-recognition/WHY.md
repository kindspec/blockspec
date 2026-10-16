# ORPHANED: rewritten to a similarity below 0.5

The anchored paragraph was replaced by a short sentence whose similarity
to it is below 0.5, so the two leftovers do not pair, and no current leaf
is a copy of the old text. 0003 §8: rewritten to similarity below 0.5,
`ORPHANED`, or refused.

SPEC.md §11.3:

> 3. **Edits.** A base leaf `i` and a current leaf `j` left over in the same
>    gap pair as `EDITED` when all of these hold: their similarity is at least
>    0.5; it exceeds the similarity of `i` to every other leftover current
>    leaf in the gap by at least 0.15; and it exceeds the similarity of `j` to
>    every other leftover base leaf in the gap by at least 0.15.

SPEC.md §11.4:

> - **No pair**: `REFUSED(unaccounted-copy)` if any current leaf is a copy of
>   `k`, and `ORPHANED` otherwise.
