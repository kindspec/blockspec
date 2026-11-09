# `#REF!`: the other branch renames the target's marker

Ours edits an unrelated paragraph. Theirs renames `#scram-threshold` to
`#trip-threshold`. The merge is clean, and the merged target has no marker of
that name. The pinned blob still has the name, so §11.9's step 1 passes, and
step 2 finds no marker: the transclusion is `#REF!(scram-threshold)`.

SPEC.md §11.9, step 2:

> 2. **The name** resolves as §8.1 says, against markers only. No match is
>    `#REF!(name)`.
