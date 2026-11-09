# `REFUSED(not-in-profile)`: a marker renamed against an edit of its paragraph

Ours edits the named paragraph and theirs renames its marker. The marker
line directly above the paragraph touches it, so stock git conflicts, and the
target keeps its conflict markers. Step 1 of §11.9 checks the current target
against the profile, and it is refused.

SPEC.md §11.9, step 1:

> 4. the current target must pass the profile, or
>       `REFUSED(not-in-profile)`;

0003 §8:

> | two branches edit the same lines | a git conflict; committed with its markers, the document is refused (`conflict-marker`) and the anchor is `REFUSED(not-in-profile)` | stale | `REFUSED(not-in-profile)` |
