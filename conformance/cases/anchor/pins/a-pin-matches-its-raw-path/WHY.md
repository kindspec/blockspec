# REFUSED(name-rebound) and RESOLVED: `./policy.md` and `policy.md` pin apart

Both links resolve to `policy.md`, but a transclusion uses the pin whose
`path` equals its own raw text. `./policy.md` is pinned to a blob from
before a paragraph was inserted after the marker, so it is
`REFUSED(name-rebound)`. `policy.md` is pinned to the current blob, so it
resolves. The pins are sorted: `.` sorts before `p`.

SPEC.md §11.9:

> - `path` is the path part of a transclusion's destination, as raw text
>   (above). A transclusion uses the pin whose `path`
>   is equal to its own.
