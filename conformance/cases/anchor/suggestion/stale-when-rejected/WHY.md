# stale: a suggestion whose status is `rejected`

The anchor resolves, and the record's status is `rejected`, not `open`.

SPEC.md §11.7:

> **A suggestion applies only when its record's `status` is `open` and its
> anchor is `RESOLVED` or `EDITED`** (0003 Q2, Q10). Otherwise it is stale. A
> suggestion is never applied on `MOVED`. An accepted or rejected suggestion
> renders as history, never as an edit that can be applied.

0003 §6:

> - **Only `open` (Q10).** Accepting a suggestion changes the document and sets
>   `status: accepted` in one commit.
