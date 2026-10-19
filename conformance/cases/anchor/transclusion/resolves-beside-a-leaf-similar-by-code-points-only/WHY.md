# RESOLVED: an unchanged pinned leaf beside a leaf similar only by code points

The named paragraph is unchanged since the pin, so it pairs `EXACT`. A new
paragraph at the end holds its text with every space replaced by a hyphen.
By code points the two are similar (`L = 70`, `T = 166`), which 0003
refused as `pinned-near-copy`. Words are split only at whitespace, so the
new paragraph is one word, which the pinned paragraph does not have: word
similarity 0. §11.9's step 3 runs §11.4, whose near-copy check on an
`EXACT` leaf uses words, so the transclusion resolves to the paragraph the
marker names, node `[2]`.

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
