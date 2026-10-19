# REFUSED(pinned-near-copy): an unchanged pinned leaf, a near-copy by words

The named paragraph is unchanged since the pin, so it pairs `EXACT`. A new
paragraph at the end holds its text with 167 digits run onto its last
word. By code points the two are just below 0.5 (`L = 83`, `T = 333`,
`4·L = 332`), which 0003 resolved. §11.9's step 3 runs §11.4, and for an
`EXACT` leaf §11.4 now compares words: thirteen of the anchored
paragraph's fourteen words are the new paragraph's first thirteen,
`L = 13`, `T = 28`, well above 0.5. The transclusion is refused.
`anchor/near-copy/exact-below-one-half-by-code-points-refuses-by-words`
is the same shape for a comment.

SPEC.md §11.2:

> The **word similarity** of two leaves (0004) is the same formula over
> words. A leaf's **words** are its `leaf.text` split at each run of U+0009,
> U+000A, U+000D and U+0020, empty pieces left out; `m` and `n` count words,
> which are compared exactly, and `L` is the length of a longest common
> subsequence of the two word sequences. It is 0 when either leaf has no
> words. Only §11.4's near-copy check on an `EXACT` leaf uses it, including
> where §11.9 runs §11.4 for a transclusion.

SPEC.md §11.9:

> 3. For each text-bearing leaf the name binds in the pinned blob, §11.3 and
>    §11.4 run with that blob as `base`. A refusal, or no pair, refuses the
>    transclusion, as `REFUSED(pinned-<reason>)`, where `<reason>` is §11.4's
>    reason or `orphaned`. Where several leaves refuse, the first in the
>    pinned blob's document order is reported.

0004, *What it gives up*:

> - **Transclusions.** SPEC.md §11.9 runs §11.4, so A also changes a pinned
>   transclusion's near-copy check. The replay does not measure
>   transclusions.
