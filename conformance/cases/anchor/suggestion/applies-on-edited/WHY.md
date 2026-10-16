# apply: an open suggestion on an EDITED anchor

The anchored paragraph's last clause changed since `base`. The anchor is
`EDITED`, which the gate admits, and the write-back goes to the hit in the
current paragraph.

SPEC.md §11.7:

> **A suggestion applies only when its record's `status` is `open` and its
> anchor is `RESOLVED` or `EDITED`** (0003 Q2, Q10). Otherwise it is stale. A
> suggestion is never applied on `MOVED`. An accepted or rejected suggestion
> renders as history, never as an edit that can be applied.
