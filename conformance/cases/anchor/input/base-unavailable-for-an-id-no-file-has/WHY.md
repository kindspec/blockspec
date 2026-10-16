# REFUSED(base-unavailable): a well-formed id that names no blob

`base` is 40 lower-case hex digits, as a SHA-1 repository's ids are, and
no blob of the repository has that id.

SPEC.md §11.10:

> | `base-unavailable` | the `base` blob, or a pin's blob, cannot be read |
