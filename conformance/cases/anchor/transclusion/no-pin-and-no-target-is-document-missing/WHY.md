# No pin and no target

READING: item 6 says a transclusion with no pin is `base-unavailable`
without giving its place in §11.9's order. This reads it as step 6 of the
inputs, where a pin's blob is read, so the missing target at step 3 is
reported first.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 6:

> Only the double-quoted title `"transclude"` makes one; `'transclude'`
> and `(transclude)` are plain paragraphs. It counts at any depth,
> inside a list item or a block quote too. A destination with no `#` is
> not a transclusion. A destination with an empty path, `#name`, is
> `REFUSED(document-missing)`. A transclusion with no pin is
> `REFUSED(base-unavailable)`.

SPEC.md, §11.9:

> **The inputs**, checked in this order; the first that fails decides
