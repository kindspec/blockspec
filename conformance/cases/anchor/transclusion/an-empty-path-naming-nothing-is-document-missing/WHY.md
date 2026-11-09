# An empty path whose name binds nothing

`dangling-link` does not reach a link titled `"transclude"`, so the referrer
is in the profile and the transclusion is refused on its own.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 6:

> Only the double-quoted title `"transclude"` makes one; `'transclude'`
> and `(transclude)` are plain paragraphs. It counts at any depth,
> inside a list item or a block quote too. A destination with no `#` is
> not a transclusion. A destination with an empty path, `#name`, is
> `REFUSED(document-missing)`. A transclusion with no pin is
> `REFUSED(base-unavailable)`.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 10:

> A paragraph, heading or table cell holding an inline link whose
> destination is `#name`, where `name` matches §7.1's name grammar and
> nothing in the document could be its target, is refused. Links are
> found by CommonMark's inline rules: code spans, autolinks and inline
> HTML bind tighter than links, a link holds no other link, and an image
> is not a link. The destination is read raw, with no escape or entity
> decoded, and may be in angle brackets. A link titled `"transclude"` is
> not read by this rule, and a cell past the header's width is dropped
> before this rule reads it.
