# REFUSED(base-unavailable): a base no commit holds any more

The record was made on a branch that was squash-merged without a
re-base, so its `base` names a blob that is not in the repository.
`squashed/policy.md` gives the blob its id and lies outside `tree/`,
`blobs/` and `merge/`, so it cannot be read.

SPEC.md §11.11:

> Once a record's `base` is gone, it is `REFUSED(base-unavailable)`.

SPEC.md §11.10:

> | `base-unavailable` | the `base` blob, or a pin's blob, cannot be read |
