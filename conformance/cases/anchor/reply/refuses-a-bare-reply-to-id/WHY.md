# REFUSED(record-inconsistent): `reply-to` not written as a JSON string

The parent's id is written bare. A reply's id is a JSON string.

SPEC.md §11.1:

> - a reply: `reply-to: ` followed by the parent's id as a JSON string, then
>   `kind: comment`.

SPEC.md §11.1:

> It is also `REFUSED(record-inconsistent)` (0003,
> addendum, detail 1) when it has no frontmatter; when the frontmatter's lines
> are not exactly those above, in that order, with nothing added; when the
> anchor or the `reply-to` id is not in the canonical form
