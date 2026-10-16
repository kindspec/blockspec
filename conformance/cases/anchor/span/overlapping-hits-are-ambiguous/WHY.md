# REFUSED(span-ambiguous): two hits that overlap

The paragraph holds a run of `trip ` fourteen times, and the span and its
full contexts lie inside the run. The current paragraph has one more
`trip ` in the run, so the span with both contexts occurs at two start
positions five code points apart, which overlap. Hits are counted by
start position, so there are two.

SPEC.md §11.5:

> Hits are counted by start position,
> overlapping ones included (§11.1). With no hit the anchor is
> `DETACHED`; with more than one, `REFUSED(span-ambiguous)`.

SPEC.md §11.1:

> **Occurrences are counted by start position** (0003, third addendum of
> 2026-10-16, item 1), here, in the consistency check below and in §11.5's
> hits alike: two occurrences that overlap are two.
