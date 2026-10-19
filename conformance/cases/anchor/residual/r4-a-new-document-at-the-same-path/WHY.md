# R4, RESOLVED: a new document at the archived document's path

`policy.md` was copied, with its notes directory, to `archive/`, and a
new `policy.md` that reuses the anchored paragraph took its place. The
suggestion left in `policy.md.notes/` resolves against the new document,
on the reused paragraph, and applies to it. Its copy in the archive
resolves against the archived document. §11.8 warns on the record id
found in two notes directories; this case kind has no field for a
warning, and the warning is not a refusal.

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

SPEC.md §11.8:

> - **A record id found in more than one notes directory is warned on** (0003
>   Q9). It is a warning, not a refusal.
