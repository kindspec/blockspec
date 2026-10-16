# REFUSED(document-missing): renamed, with the notes left behind

`policy.md` was renamed to `rules.md` and its notes directory was not
moved with it. The directory, not the record, says which document a
record belongs to, and `policy.md` does not exist. 0003 §8: renamed
without its notes directory, `REFUSED(document-missing)`.

SPEC.md §11.1:

> **A comment or a suggestion is a record: one file per record, in
> `<doc>.notes/` beside its document** (0003 Q1). For `policy.md` that is
> `policy.md.notes/`. The directory is authoritative for which document a
> record belongs to, and a record holds no path (0003 Q9).

SPEC.md §11.8:

> - **A commit that renames a document moves its notes directory in the same
>   commit** (0003 Q9).

SPEC.md §11.10:

> | `document-missing` | the notes directory's document, or a transclusion's target, does not exist |
