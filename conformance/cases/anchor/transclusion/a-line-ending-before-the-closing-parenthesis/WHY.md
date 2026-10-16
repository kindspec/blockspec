# RESOLVED: a line ending between the title and `)`

The link's title is followed by a line ending and then `)`. CommonMark
allows whitespace, one line ending included, there, so the paragraph is
still exactly one link titled `transclude`, and it resolves.

SPEC.md §11.9:

> **A transclusion is a paragraph whose content is exactly one inline link
> with the title `transclude`** (0003 Q5)

CommonMark 0.31.2, *Links*:

> An [inline link](@) consists of a [link text] followed immediately
> by a left parenthesis `(`, an optional [link destination], an optional
> [link title], and a right parenthesis `)`.
> These four components may be separated by spaces, tabs, and up to one line
> ending.
