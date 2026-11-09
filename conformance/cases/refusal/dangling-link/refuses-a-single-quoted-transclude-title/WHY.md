# A single-quoted `transclude` title

Item 6 makes this a plain paragraph, not a transclusion, so its link is read
here.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 10:

> A paragraph, heading or table cell holding an inline link whose
> destination is `#name`, where `name` matches §7.1's name grammar and
> resolves to `#REF!(name)` under §8, is refused. Text inside a code
> span is not a link. A link titled `"transclude"` is a transclusion and
> is read under §11.9. A destination that does not start with `#`, or
> whose name does not match the grammar, is not read.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 6:

> Only the double-quoted title `"transclude"` makes one; `'transclude'`
> and `(transclude)` are plain paragraphs. It counts at any depth,
> inside a list item or a block quote too. A destination with no `#` is
> not a transclusion. A destination with an empty path, `#name`, is
> `REFUSED(document-missing)`. A transclusion with no pin is
> `REFUSED(base-unavailable)`.
