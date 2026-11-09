# A region containing the heading with its slug

The heading is one of the region's nodes, so the marker and the heading are
the same target. Markers resolve first, so the name resolves to the region.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 11:

> A marker whose name is the slug of a heading it does not bind is
> refused. Markers resolve first (§8.1), so such a marker silently takes
> the name from the heading. A one-line marker directly above that
> heading binds it and is allowed, and so is a region whose nodes
> include that heading. Two headings sharing the slug are both read: a
> marker binding one of them still does not bind the other.
