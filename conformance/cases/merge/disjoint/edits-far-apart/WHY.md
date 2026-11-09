# Two branches edit blocks far apart

The first and last paragraphs change, sixteen lines apart, with a region in
the middle. The merge touches neither the region nor its markers: the region
still holds the two paragraphs between them, read as §7.3 reads it.

SPEC.md §7.3:

> **A `:begin` / `:end` pair binds `name` to the sibling nodes between its two
> markers.**
