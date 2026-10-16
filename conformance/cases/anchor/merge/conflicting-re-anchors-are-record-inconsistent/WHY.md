# REFUSED(record-inconsistent): two re-anchorings conflict

Two branches re-anchor the same record onto different blobs. Each rewrites
the whole `anchor:` line, so stock git conflicts, and the record committed
with its markers has frontmatter lines that are not the grammar's.

0003 §3:

> - **The anchor is one line.** A re-anchoring tool rewrites the whole line.
>   Two concurrent re-anchorings then conflict, where a multi-line anchor could
>   be merged line by line into a record that matches neither side.

SPEC.md §11.1:

> It is also `REFUSED(record-inconsistent)` (0003,
> addendum, detail 1) when it has no frontmatter; when the frontmatter's lines
> are not exactly those above, in that order, with nothing added;
