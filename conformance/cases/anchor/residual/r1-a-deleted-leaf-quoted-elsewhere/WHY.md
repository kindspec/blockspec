# R1, MOVED: a paragraph deleted, and its wording quoted in an appendix

The anchored paragraph was deleted, and its exact wording added under a
`Superseded wording` heading at the end. The snapshots are those of a real
move, so the comment follows the quote as `MOVED`. The suggestion is stale,
because a suggestion never applies on `MOVED`: R1 does not reach
suggestions.

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

SPEC.md §11.7:

> **A suggestion applies only when its record's `status` is `open` and its
> anchor is `RESOLVED` or `EDITED`** (0003 Q2, Q10). Otherwise it is stale. A
> suggestion is never applied on `MOVED`. An accepted or rejected suggestion
> renders as history, never as an edit that can be applied.
