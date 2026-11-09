# A table with a line directly below it, which only the merge produces

Ours turns `| x |` into a delimiter row, a table with a blank line below,
accepted. Theirs replaces that blank line with `More text.`, and with no
delimiter row its lines are one paragraph, accepted too. The unchanged last row
keeps the edits apart, so stock git merges them, and the merged table has a
non-blank line directly below it.

SPEC.md §4.3:

> - a table with a non-blank line directly below it in its container is
>   refused (`table-not-blank-below`). A non-blank line directly after a
>   table's rows that markdown-it reads as one more row and pandoc as a
>   paragraph is this refusal (0002, addendum on ambiguous tables);
