# A table with a line directly above it, which only the merge produces

Ours turns `| x |` into a delimiter row, so lines 3 to 5 become a table with a
blank line above it, which is accepted. Theirs replaces the blank line above
with `Extra.`; with no delimiter row its lines are one paragraph, accepted too.
The unchanged header line keeps the edits apart, so stock git merges them, and
the merged text is a table with a non-blank line directly above it.

SPEC.md §4.3:

> - a table with a non-blank line directly above it in its container is
>   refused (`table-not-blank-above`);
