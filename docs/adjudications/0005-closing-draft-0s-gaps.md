<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Adjudication 0005: closing draft 0's gaps before its first release

A second implementation, written from `SPEC.md` alone, and merge cases that
run stock git, showed where the text left a choice to whoever implemented it,
and two merges the format could catch and did not. This document decides them.
Owner, 2026-11-09.

## Decision

**1. An escaped pipe.** A `|` is escaped when the character directly before it
is a backslash, however many backslashes come before that one. This is how
cmark-gfm's scanner and markdown-it read it.

**2. A table's delimiter line** indented four or more columns is not a
delimiter line. It continues the paragraph above.

**3. What a table row is.** A non-blank line directly below a table's rows is
another row when it holds an unescaped pipe, starts no other block, and is not
only `|` with spaces or tabs around it. A line that is a row in markdown-it's reading
and not by this rule stays `table-not-blank-below`.

**4. Frontmatter's closing line is an edge.** A table directly below it has
its container's edge above it, and is not `table-not-blank-above`.

**5. An empty list item,** for deciding whether it may interrupt a paragraph,
is one whose first line after the marker holds only spaces and tabs,
CommonMark's blank. A form feed is not blank.

**6. Transclusions.** Only the double-quoted title `"transclude"` makes one;
`'transclude'` and `(transclude)` are plain paragraphs. It counts at any depth,
inside a list item or a block quote too. A destination with no `#` is not a
transclusion. A destination with an empty path, `#name`, is
`REFUSED(document-missing)`. A transclusion with no pin is
`REFUSED(base-unavailable)`.

**7. Suggestions.** On a table, an open suggestion whose anchor is `RESOLVED` or
`EDITED` is stale with the reason `unmappable-offset`. A `\n` in `replace` breaks the line where the span
starts, and the result is not re-checked against the profile when it is
written.

**8. A heading whose slug comes out empty has no slug**, as `# !!!` has none. A
reference to it is `#REF!(name)`, and so is the empty name.

**9. §11.7's prefix.** The content before the span is read from the leaf the
anchor is paired with in the current document, not from the record's stored
base text.

**10. `dangling-link`, a new refusal.** A paragraph, heading or table cell
holding an inline link whose destination is `#name`, where `name` matches
§7.1's name grammar and resolves to `#REF!(name)` under §8, is refused. Text
inside a code span is not a link, a link titled `"transclude"` is not read by
this rule, and a cell past the header's width is dropped before this rule
reads it. A destination that does not start with
`#`, or whose name does not match the grammar, is not read.

This is the one place the profile looks inside inline content for a reason
other than transclusion. One branch deleting a section while another keeps a
link to it merges clean, and the file then says something false that nothing
reports.

**11. `name-shadows-slug`, a new refusal.** A marker whose name is the slug of
a heading it does not bind is refused. Markers resolve first (§8.1), so such a
marker silently takes the name from the heading. A one-line marker directly
above that heading binds it and is allowed, and so is a region whose nodes
include that heading. Two headings sharing the slug are both read: a marker
binding one of them still does not bind the other. This narrows 0001's
"markers first": that order now decides only where the marker and the heading
are the same target.

## Left open

A byte-order mark, bytes that are not UTF-8, and the other items §12 still
lists, are not decided here.
