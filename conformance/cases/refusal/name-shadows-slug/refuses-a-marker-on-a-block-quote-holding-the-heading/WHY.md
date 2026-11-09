# A marker on a block quote holding the heading

READING: §7.2 binds the marker to the next sibling node, here the block
quote, and item 11 allows the marker "directly above that heading". The
heading is inside the bound node and is not the bound node, so this reads it
as not bound. 0005 does not say whether binding a container binds what it
holds.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 11:

> A marker whose name is the slug of a heading it does not bind is
> refused. Markers resolve first (§8.1), so such a marker silently takes
> the name from the heading. A one-line marker directly above that
> heading binds it and is allowed, and so is a region whose nodes
> include that heading. Two headings sharing the slug are both read: a
> marker binding one of them still does not bind the other.

SPEC.md, §7.2:

> **`<!-- #name -->` binds `name` to the next sibling node in its
> container**, at any depth (0001; 0002 §3).
