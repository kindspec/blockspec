# R2, RESOLVED: rewritten beyond recognition, the old wording quoted below

The anchored paragraph was rewritten into a short sentence, and a block
quote of its old wording sits directly below it. The quote's paragraph has
the old key, in the old paragraph's place in the chain, so it is the
anchored leaf, `EXACT`, and the rewrite is a new leaf too unlike it to be
a near-copy. Since 0004 that is judged by words for an `EXACT` leaf: the
rewrite shares seven of its eight words with the old paragraph's
thirty-three (`L = 7`, `T = 41`), below 0.5; by code points it is below 0.5
too (`L = 48`, `T = 250`), so the outcome is 0003's. The comment resolves
on the quotation, and the suggestion applies to it.
`residual/r2-a-rewrite-below-one-half-by-words-only` is the form 0004
widens R2 to.

**This outcome is a documented residual, not a defect.** §11.12 lists it
among the edits no resolver that reads only `base` and the current text
can tell from a legitimate one, so the case pins the resolution the rules
give, which is silently wrong for the history described here and right
for its twin.

SPEC.md §11.12:

> Four mechanisms leave current bytes identical to those a legitimate edit
> produces, so they resolve, silently, to the wrong text (0003 §9, with R2
> and R3 as 0004 widens them):
>
> | | mechanism | indistinguishable from | suggestions |
> | --- | --- | --- | --- |
> | R1 | a leaf deleted, and a verbatim copy of it elsewhere | a move | not affected: stale on `MOVED` |
> | R2 | a leaf rewritten to word similarity below 0.5 (0004; by code points it may be more similar), with a verbatim copy of its old text left in its place in order | a new leaf inserted beside an unchanged one | affected |
> | R3 | inside one leaf, the span's sentence rewritten and the old sentence re-added with its neighbouring code points and the sides of its context §11.5 requires: for a comment where both leaves are `p` or headings, one side, compared with whitespace runs as one space (0004) | a sentence moved within its leaf | affected |
> | R4 | a different document at the same path, by archive-and-replace or copy-and-rewrite | an edit of the document | affected |
