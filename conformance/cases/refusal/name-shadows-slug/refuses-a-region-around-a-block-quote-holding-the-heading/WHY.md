# A region around a block quote holding the heading

READING: §7.3 makes a region's nodes the sibling nodes between its markers.
The heading is inside one of those nodes and is not one of them, so "a
region whose nodes include that heading" is read as not covering it. Same
open question as the one-line case.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 11:

> A marker whose name is the slug of a heading it does not bind is
> refused. Markers resolve first (§8.1), so such a marker silently takes
> the name from the heading. A one-line marker directly above that
> heading binds it and is allowed, and so is a region whose nodes
> include that heading. Two headings sharing the slug are both read: a
> marker binding one of them still does not bind the other.

SPEC.md, §7.3:

> **A `:begin` / `:end` pair binds `name` to the sibling nodes between
> its two markers.**
