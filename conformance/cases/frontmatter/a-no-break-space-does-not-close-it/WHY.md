0002, Addendum (three defaults): "**Frontmatter is closed by a line of
`---` followed only by spaces or tabs**, as pandoc reads a YAML metadata
block, and never by YAML's `...` document end marker. The opening line is
exactly `---`."
Line 3 is `---` followed by U+00A0, a no-break space (bytes C2 A0), which
is not a space or a tab, so it does not close the frontmatter. No other
line does, so this is not frontmatter (README reading 11), and the lines
parse as CommonMark 0.31.2:

- line 1 is a thematic break (§4.1);
- line 3 is neither a setext underline nor a thematic break. §4.3 allows a
  setext underline only "trailing spaces or tabs", §4.1 allows a thematic
  break only spaces or tabs between and after its characters, and §2.1
  defines a space as U+0020. So it is paragraph continuation text, the
  document is not refused as a setext heading, and lines 2 to 4 are one
  paragraph. Paragraph content strips only spaces or tabs, so the no-break
  space stays.

pandoc 3.1.11.1 (`-f commonmark`) and markdown-it-py 3.0.0 read the same.
A reader that let any whitespace close the frontmatter would report
frontmatter on lines 1 to 3.
