# A one-line marker directly after its heading

The next-sibling allowance is for a region's `:begin`. A one-line marker
binds the paragraph after it.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 11:

> A marker whose name is the slug of a heading it does not bind is
> refused. Markers resolve first (§8.1), so such a marker silently takes
> the name from the heading. A one-line marker directly above that
> heading binds it and is allowed, and so is a region whose nodes
> include that heading, or whose `:begin` is the next sibling after it.
> Two headings sharing the slug are both read: a marker binding one of
> them still does not bind the other.
