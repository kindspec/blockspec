# R2, RESOLVED: a rewrite similar by code points but not by words, the old text in place

The anchored paragraph's old text is still in its place, and a
re-punctuated version of it sits below. If the history is that the
paragraph was rewritten and a verbatim copy of its old text left in place,
the descendant is the re-punctuated one; the snapshots are also those of a
new paragraph added beside an unchanged one. The old text keeps its key,
so it is the anchored leaf, `EXACT`. The new paragraph's word similarity to
it is 0.25 (one word of eight in common), below 0.5, so no near-copy
refuses it, though by code points it is above 0.9 (`L = 36`, `T = 78`),
which 0003 refused. The comment resolves and the suggestion applies on the
old text.

**This outcome is a documented residual, not a defect.** §11.12's R2,
which 0004 widens to word similarity, so the case pins the resolution the
rules give, which is silently wrong for the history described here and
right for its twin.

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

0004, *What it gives up*:

> - **R2** is a leaf rewritten beyond recognition with its old wording left
>   in order, and "beyond recognition" is now in words for the near-copy
>   check: a rewrite below 0.5 by words resolves onto the copy even where its
>   code points reach 0.5, and one at 0.5 by words but below by code points
>   now refuses.
