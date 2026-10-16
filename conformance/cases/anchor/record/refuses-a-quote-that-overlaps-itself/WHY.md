# REFUSED(record-inconsistent): the quote occurs at overlapping positions

The paragraph repeats `trip ` twenty times. The record's `prefix + span +
suffix` is 68 code points of that run, so it starts at 6 positions,
each overlapping the next. Counted by start position, it does not occur
exactly once, though a count of non-overlapping matches would find one.

SPEC.md §11.1:

> **Occurrences are counted by start position** (0003, third addendum of
> 2026-10-16, item 1), here, in the consistency check below and in §11.5's
> hits alike: two occurrences that overlap are two.

SPEC.md §11.1:

> **Consistency.** A record is `REFUSED(record-inconsistent)` when `leaf` at
> `nth` is not in `base`; when `prefix + span + suffix` does not occur exactly
> once in `leaf.text`; when `prefix` or `suffix` is shorter than 32 code points
> while the leaf's edge is further away; or when `span` is empty (0003, the
> details it fixes).
