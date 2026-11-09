# `REFUSED(name-rebound)`: the other branch moves the marker to the next paragraph

Theirs moves the marker from the pinned paragraph to the paragraph below. The
merge is clean, the pinned leaf is unchanged and still pairs `EXACT`, but it no
longer lies inside what the name binds.

SPEC.md §11.9, step 4:

> 4. Each pair must lie inside what the name binds now. Otherwise the
>    transclusion is `REFUSED(name-rebound)`.
