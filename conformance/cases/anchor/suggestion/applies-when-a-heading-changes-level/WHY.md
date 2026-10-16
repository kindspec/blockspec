# apply: a heading that only changed level

The suggestion is on the heading's first word, and the heading went from
level 1 to level 2. 0003 §8: a heading changes level only, `EDITED`, and
the suggestion applies.

SPEC.md §11.7:

> **A suggestion applies only when its record's `status` is `open` and its
> anchor is `RESOLVED` or `EDITED`** (0003 Q2, Q10). Otherwise it is stale. A
> suggestion is never applied on `MOVED`. An accepted or rejected suggestion
> renders as history, never as an edit that can be applied.
