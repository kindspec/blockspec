# R2, RESOLVED: rewritten beyond recognition, the old wording quoted below

The anchored paragraph was rewritten into a short sentence, similarity
below 0.5, and a block quote of its old wording sits directly below it.
The quote's paragraph has the old key, in the old paragraph's place in the
chain, so it is the anchored leaf, `EXACT`, and the rewrite is a new leaf
too unlike it to be a near-copy. The comment resolves on the quotation, and
the suggestion applies to it.

**This outcome is a documented residual, not a defect.** §11.12 lists it
among the edits no resolver that reads only `base` and the current text
can tell from a legitimate one, so the case pins the resolution the rules
give, which is silently wrong for the history described here and right
for its twin.

SPEC.md §11.12:

> Four mechanisms leave current bytes identical to those a legitimate edit
> produces, so they resolve, silently, to the wrong text (0003 §9):
>
> | | mechanism | indistinguishable from | suggestions |
> | --- | --- | --- | --- |
> | R1 | a leaf deleted, and a verbatim copy of it elsewhere | a move | not affected: stale on `MOVED` |
> | R2 | a leaf rewritten to similarity below 0.5, with a verbatim copy of its old text left in its place in order | a new leaf inserted beside an unchanged one | affected |
> | R3 | inside one leaf, the span's sentence rewritten and the old sentence re-added with the same context | a sentence moved within its leaf | affected |
> | R4 | a different document at the same path, by archive-and-replace or copy-and-rewrite | an edit of the document | affected |
