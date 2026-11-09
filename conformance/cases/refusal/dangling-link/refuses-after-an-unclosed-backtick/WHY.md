# A dangling link after a lone backtick

The backtick has no partner, so there is no code span and the link is a link
(CommonMark 0.31.2 §6.1).

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
