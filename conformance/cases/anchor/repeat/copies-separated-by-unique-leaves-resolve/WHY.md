# RESOLVED: two copies, each between unchanged unique neighbours

The paragraph `R` occurs twice in both snapshots, once between `I` and `B`
and once after `B`. A comment on each copy (`nth` 0 and 1) stays on that
copy: each gap holds one copy on both sides, and the gap's alignment pairs
them. The last paragraph was edited, which leaves `B` the last chain pair.
0003 §8: identical copies separated by unchanged unique leaves, `RESOLVED`
on the right copy.

SPEC.md §11.3:

> 2. **Gaps.** The chain cuts each snapshot into gaps: the leaves between two
>    consecutive chain pairs, before the first, or after the last, leaving out
>    leaves paired as `MOVED`. Inside each gap, the longest common subsequence
>    alignment (§11.2) of the base leaves' keys onto the current leaves' keys
>    gives further `EXACT` pairs.

SPEC.md §11.4:

> - **`EXACT`**:
>   - if `base` or the current text holds more than one copy of `k`, the
>     number of copies in `k`'s gap must be equal on both sides, or
>     `REFUSED(repeat)`. The pair always lies in the gap: a repeated key is
>     never on the chain, so `k`'s `EXACT` pair comes from §11.3 step 2's
>     alignment inside `k`'s own gap (0003, second addendum of 2026-10-16,
>     item 9);
