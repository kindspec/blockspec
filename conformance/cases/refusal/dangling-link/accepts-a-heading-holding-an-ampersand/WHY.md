# A link to a heading holding `&`

READING: §8.2 gives a heading holding `&` no slug, and item 10 names only
`*`, `_` and backticks as also removed. Item 10 still says "any heading" and
that it slugs "as §8.2 does", and §8.2's character class removes `&`. This
reads the no-slug exception as not carried over, so the slug is `qa`.

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

docs/adjudications/0005-closing-draft-0s-gaps.md, item 10, a possible target:

> the GitHub slug of any heading: its raw content with inline HTML tags
> removed and each `[text](destination)` reduced to `text`, slugged as
> §8.2 does but also with `*`, `_` and backticks removed, so a heading
> holding them still counts.

SPEC.md, §8.2:

> a heading whose raw content holds `*`, `_`, `` ` ``, `[`, `<` or `&`
> has no slug
