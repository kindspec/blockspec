# REFUSED(record-inconsistent): a 33-code-point prefix

The span `sigma` starts at code point 35, and the record stores the 33 code
points before it as its prefix. A context is exactly 32 code points, or
fewer only at the leaf's edge.

SPEC.md §11.1:

> And it is
> `REFUSED(record-inconsistent)` (0003, second addendum of 2026-10-16) when
> `prefix` or `suffix` is longer than 32 code points (item 1); when its
> `reply-to` string is not a ULID in the form above (item 5); or when the
> profile refuses its body (item 8), since a record is a blockspec document.
