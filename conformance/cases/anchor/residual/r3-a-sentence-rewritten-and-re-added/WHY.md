# R3, EDITED: the span's sentence rewritten, and re-added with its context

The sentence holding the span was rewritten in place, and the old
sentence re-added at the paragraph's end. The span's 32-code-point
contexts lie inside that sentence, so the re-added copy is the one hit,
and the tail after the rewritten sentence is short, so the longest common
subsequence alignment carries the old sentence onto the copy. The
snapshots are those of a sentence moved within its paragraph and a new
one written where it was. The comment lands on the copy, `EDITED`, and
the suggestion applies there. `span/the-alignment-detaches-a-rewritten-span`
is the same edit after a long tail, which detaches.

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

SPEC.md §11.5:

> With one hit, the
> longest common subsequence alignment (§11.2) of the base leaf's text onto
> the paired leaf's text must pair every code point of the span with the code
> point at the same position in the hit, or the anchor is `DETACHED` (0003
> §5).
