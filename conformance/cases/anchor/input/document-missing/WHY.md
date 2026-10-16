# REFUSED(document-missing): no document beside the notes directory

The record sits in `policy.md.notes/`, and the current tree has no
`policy.md`. Its `base` is still readable, and the record is consistent
with it. 0003 §8: the document deleted, `REFUSED(document-missing)`.

SPEC.md §11.1:

> **A comment or a suggestion is a record: one file per record, in
> `<doc>.notes/` beside its document** (0003 Q1). For `policy.md` that is
> `policy.md.notes/`. The directory is authoritative for which document a
> record belongs to, and a record holds no path (0003 Q9).

SPEC.md §11.10:

> | `document-missing` | the notes directory's document, or a transclusion's target, does not exist |
