# stale: the span did not survive

Someone else already changed the span. The anchor is `DETACHED`, so the
suggestion does not apply. The reason is `null`: only a failed mapping is
`unmappable-offset`.

SPEC.md §11.7:

> **A suggestion applies only when its record's `status` is `open` and its
> anchor is `RESOLVED` or `EDITED`** (0003 Q2, Q10). Otherwise it is stale. A
> suggestion is never applied on `MOVED`. An accepted or rejected suggestion
> renders as history, never as an edit that can be applied.
