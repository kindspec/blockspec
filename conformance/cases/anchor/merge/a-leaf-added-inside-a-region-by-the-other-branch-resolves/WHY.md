# `RESOLVED`: a leaf added inside a pinned region by the other branch

Ours adds a paragraph inside the region, and theirs edits a paragraph
elsewhere. The merge is clean. The one pinned leaf pairs `EXACT`, and lies
inside the region. Step 3 runs over the leaves the name bound in the pinned
blob and step 4 over their pairs, and neither looks at a leaf the region did not
hold when it was pinned. So the transclusion resolves and the new paragraph is
transcluded with no re-pin.

This is one of the silently wrong merges reported with this set: the unit a
referrer receives has changed, and its status says `RESOLVED`.

SPEC.md §11.9, steps 3 and 4:

> 3. For each text-bearing leaf the name binds in the pinned blob, §11.3 and
>    §11.4 run with that blob as `base`.

> 4. Each pair must lie inside what the name binds now.

And §11.9, on the unit:

> **The unit transcluded is what the name binds** (0002 §4): one node with its
> subtree, or the nodes of one region.
