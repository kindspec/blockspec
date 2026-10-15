0002, Addendum (three defaults): "**Frontmatter is closed by a line of
`---` followed only by spaces or tabs**, as pandoc reads a YAML metadata
block, and never by YAML's `...` document end marker. The opening line is
exactly `---`."
Line 3 is `---` followed by a form feed, so it does not close the
frontmatter, and with no other closing line this is not frontmatter
(README reading 11). Line 1 is a thematic break. Line 3 is neither a
setext underline nor a thematic break (CommonMark 0.31.2 §4.3, §4.1, §2.1),
so lines 2 to 4 are one paragraph, with the form feed kept.
Line 2 holds a pipe, so it is not the pipe-less header of the
ambiguous-table refusal, and with two header cells over a one-cell
delimiter row it is no table to GitHub either (GFM 0.29-gfm §4.10).
pandoc 3.1.11.1 (`-f gfm`, `-f commonmark`) and markdown-it-py 3.0.0 read
a thematic break and one paragraph. This keeps "a form feed does not close
frontmatter" pinned. An earlier case with the pipe-less line 2 `a: 1` was
removed when ambiguous-table widened, because both ambiguous-table and
table-not-blank-below apply to it, in an order the addenda do not fix.
