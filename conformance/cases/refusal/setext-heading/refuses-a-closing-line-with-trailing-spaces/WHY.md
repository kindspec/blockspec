READING 9: frontmatter ends at a later line that is exactly `---`. Line 3
is `---` followed by two spaces, so it does not close the frontmatter, and
with no other closing line this is not frontmatter (READING 11). Its lines
parse under the existing rules: line 1 is a thematic break, and line 3,
which may carry trailing spaces as a setext underline (CommonMark 0.31.2
§4.3), turns line 2 into a setext heading, which 0001 refuses.
