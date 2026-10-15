The owner's decision of 2026-10-14 (0002, addendum): frontmatter is
opened by `---` on line 1 and closed by `---`. READING 9: it ends at the
first later line that is `---`, optionally followed by spaces or
tabs. Here two later lines qualify, so
the frontmatter is lines 1 to 3, and the `---` on line 6, after a blank
line, is a thematic break (CommonMark 0.31.2 §4.1).
frontmatter/the-first-closing-line-ends-it has only one later `---` line,
so it cannot tell the first closing line from the last.
