0002, Addendum (ambiguous tables), "two more table edges": a row consisting only of `|` (or ` |`) ends a
table, so it is a non-blank line directly below it, which 0002 §6 refuses.
markdown-it reads the line as one more (empty) row, and pandoc's `gfm`
reader as a paragraph, the disagreement §6 refuses.
