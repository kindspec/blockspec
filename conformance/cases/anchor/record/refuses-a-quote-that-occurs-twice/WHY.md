# REFUSED(record-inconsistent): `prefix + span + suffix` occurs twice

The paragraph repeats a clause, and the span with its 32-code-point prefix
and suffix lies inside the clause, so the three occur twice in the leaf.

SPEC.md §11.1:

> **Consistency.** A record is `REFUSED(record-inconsistent)` when `leaf` at
> `nth` is not in `base`; when `prefix + span + suffix` does not occur exactly
> once in `leaf.text`; when `prefix` or `suffix` is shorter than 32 code points
> while the leaf's edge is further away; or when `span` is empty (0003, the
> details it fixes).
