# A blank line between the marker and its heading

READING: item 11 says "directly above", but its rule is whether the marker
binds the heading, and §7.2 says a blank line does not change what it binds.
The marker binds this heading, so it is accepted.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 11:

> A marker whose name is the slug of a heading it does not bind is
> refused. Markers resolve first (§8.1), so such a marker silently takes
> the name from the heading. A one-line marker directly above that
> heading binds it and is allowed, and so is a region whose nodes
> include that heading, or whose `:begin` is the next sibling after it.
> Two headings sharing the slug are both read: a marker binding one of
> them still does not bind the other.

SPEC.md, §7.2:

> A blank line between the marker and the node does not matter.
