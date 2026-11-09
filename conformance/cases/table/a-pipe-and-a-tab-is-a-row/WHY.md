# A lone pipe followed by a tab

READING: item 3 excludes a line that is only `|` "with spaces around it".
Item 5 of the same adjudication names "spaces and tabs" separately, so this
reads "spaces" as U+0020 only: a tab keeps the line a row. The row's one
empty cell is padded to the header's width.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 3:

> A non-blank line directly below a table's rows is another row when it
> holds an unescaped pipe, starts no other block, and is not only `|`
> with spaces around it. A line that is a row in markdown-it's reading
> and not by this rule stays `table-not-blank-below`.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 5:

> **5. An empty list item** is one whose first line after the marker
> holds only spaces and tabs, CommonMark's blank. A form feed is not
> blank.
