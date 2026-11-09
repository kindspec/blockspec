# Each branch deletes one block of a region, leaving an empty region

Ours deletes the region's first paragraph, theirs the second. Each branch alone
keeps a region with one paragraph in it. The merge is clean, since the deletions
are separated by a blank line, and leaves the two markers with nothing between
them.

SPEC.md §7.3:

> A `:begin` directly followed by its
> `:end`, with no node between them, is an empty region, refused as
> `dangling-marker` (§7.2).
