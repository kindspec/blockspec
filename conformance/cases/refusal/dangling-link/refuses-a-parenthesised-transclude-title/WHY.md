# A parenthesised `transclude` title

READING: item 10 says a link titled `"transclude"` is not read, and writes
the title with its double quotes, as item 6 does when it separates that form
from `'transclude'` and `(transclude)`. This reads item 10 as meaning the
double-quoted form only, so this link is read.

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

docs/adjudications/0005-closing-draft-0s-gaps.md, item 6:

> Only the double-quoted title `"transclude"` makes one; `'transclude'`
> and `(transclude)` are plain paragraphs.
