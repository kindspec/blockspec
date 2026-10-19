# R3, EDITED for the comment, DETACHED for the suggestion: a re-added sentence with one side of its context

As `residual/r3-a-sentence-rewritten-and-re-added`, but the re-added
sentence is shorter: it ends `above baseline.`, so the span's
32-code-point suffix, ` above the rolling baseline for `, no longer
follows it. Its 32-code-point prefix, ` trips when its reading exceeds `,
does precede it, and the span has a space on each side. For a comment on
a paragraph that one side is enough, so the re-added copy is the one hit,
and the alignment carries the span there: `EDITED`. The suggestion needs
both sides: `DETACHED`, and stale. Under 0003 the comment detached too.

**This outcome is a documented residual, not a defect.** §11.12's R3,
which 0004 widens to one side of the context for a comment on prose, so
the case pins the resolution the rules give, which is silently wrong for
the history described here and right for its twin, a sentence moved
within its paragraph and shortened.

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

> - **R3** is a sentence rewritten and the old one re-added in the same leaf;
>   a comment now follows the re-added copy when one side of its context and
>   its neighbours hold, where 0003 needed both sides. A suggestion still
>   needs both.

SPEC.md §11.5:

> Hits are counted by start position,
> overlapping ones included (§11.1). With no hit the anchor is
> `DETACHED`; with more than one, `REFUSED(span-ambiguous)`. With one hit, the
> longest common subsequence alignment (§11.2) of the base leaf's text onto
> the paired leaf's text must pair every code point of the span with the code
> point at the same position in the hit, or the anchor is `DETACHED` (0003
> §5).
