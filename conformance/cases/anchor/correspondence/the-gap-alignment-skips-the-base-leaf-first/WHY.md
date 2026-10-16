# EDITED: the gap alignment's tie-break, on two swapped twins

`X` and `Y` each occur twice, so only the heading, `Alpha` and `Bravo` are
unique, and they form the chain. In the gap after `Alpha`, `base` has
`X, Y` and the current text `Y, X`. Their longest common subsequence has
length 1, either key. The alignment compares `X` with `Y`; skipping the
base element `X` does not shorten the longest common subsequence of what
remains, so `X` is skipped and `Y` pairs with `Y` as `EXACT`. The anchored
`X` (`nth` 0) is left over with the current `X`, its copy, and they pair as
`EDITED`, similarity 1. No unmatched leaf remains, and the text is
unchanged, so the span is found. An alignment that skipped the current
element first would pair the two `X`s as `EXACT` instead.

SPEC.md §11.2:

> A **longest common subsequence alignment** of two sequences pairs elements
> from the start: when the two elements under consideration are equal they
> are paired;
> otherwise the element of the first sequence is skipped if that does not
> shorten the longest common subsequence of what remains, and the element of
> the second is skipped if it does.

SPEC.md §11.3:

> 2. **Gaps.** The chain cuts each snapshot into gaps: the leaves between two
>    consecutive chain pairs, before the first, or after the last, leaving out
>    leaves paired as `MOVED`. Inside each gap, the longest common subsequence
>    alignment (§11.2) of the base leaves' keys onto the current leaves' keys
>    gives further `EXACT` pairs.

SPEC.md §11.3:

> 3. **Edits.** A base leaf `i` and a current leaf `j` left over in the same
>    gap pair as `EDITED` when all of these hold: their similarity is at least
>    0.5; it exceeds the similarity of `i` to every other leftover current
>    leaf in the gap by at least 0.15; and it exceeds the similarity of `j` to
>    every other leftover base leaf in the gap by at least 0.15.
