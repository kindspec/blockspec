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

**Under 0004** the near-copy rule compares the word similarity. The
anchored paragraph has 34 words (`p` and 33 pieces of text); the new
document's other paragraphs share at most `p` and `the` with it (`This
revision replaces the archived policy.`: `2·2/41`; `Further rules
follow.`: `2·1/38`), and its heading shares no word (its first word is
`h1`), all below 0.5. The outcome is unchanged.

SPEC.md §11.12:

> Four mechanisms leave current bytes identical to those a legitimate edit
> produces, so they resolve, silently, to the wrong text (0003 §9):
>
> | | mechanism | indistinguishable from | suggestions |
> | --- | --- | --- | --- |
> | R1 | a leaf deleted, and a verbatim copy of it elsewhere | a move | not affected: stale on `MOVED` |
> | R2 | a leaf rewritten to word similarity below 0.5 (0004; by code points the rewrite may be more similar), with a verbatim copy of its old text left in its place in order | a new leaf inserted beside an unchanged one | affected |
> | R3 | inside one leaf, the span's sentence rewritten and the old sentence re-added with one side of its context or both (0004), on the same word boundaries | a sentence moved within its leaf | affected |
> | R4 | a different document at the same path, by archive-and-replace or copy-and-rewrite | an edit of the document | affected |

SPEC.md §11.8:

> - **A record id found in more than one notes directory is warned on** (0003
>   Q9). It is a warning, not a refusal.
