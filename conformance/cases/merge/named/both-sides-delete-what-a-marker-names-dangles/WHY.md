# A merge separates a marker from everything it could name

Ours deletes `One.` and the name binds `Two.`; theirs deletes `Two.` and the
name binds `One.`. Each branch alone is accepted. The two deletions are one
unchanged line apart, so stock git merges them, and the merged text is a marker
with nothing after it: `dangling-marker`, as §7.2 refuses it.

SPEC.md §7.2:

> These are refused as `dangling-marker`:
>
> - a one-line marker with no next sibling in its container;
