# A code span that takes part of the link's syntax

Code spans bind tighter than links (CommonMark 0.31.2 §6.3), so the
backticks pair and there is no link.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 10:

> A paragraph, heading or table cell holding an inline link whose
> destination is `#name`, where `name` matches §7.1's name grammar and
> resolves to `#REF!(name)` under §8, is refused. Text inside a code
> span is not a link. A link titled `"transclude"` is a transclusion and
> is read under §11.9. A destination that does not start with `#`, or
> whose name does not match the grammar, is not read.
