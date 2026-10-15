Owner's ruling, 2026-10-14: a delimiter-like row that begins with `- `
is a bullet list item, because the table start is tried after list items,
in cmark-gfm's order. A non-empty bullet item may interrupt a paragraph
(CommonMark 0.31.2 §5.2), so line 1 is a paragraph and line 2 a list whose
item holds the paragraph `| -`. pandoc's `gfm` reader and markdown-it agree.
