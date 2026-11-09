# A marker after a partly consumed tab in a list item

`2.` starts an item whose first line is blank, so its content column is 3.
The tab on line 2 reaches column 4; the item takes three columns and one is
left as a space, which CommonMark keeps. That is one column of indentation,
under the marker line's limit of three, so the line is a marker. An HTML
block keeps its initial spaces, so the content starts with that one space.
`x` at column 3 is the next sibling, and the marker binds it.

SPEC.md, §7.1:

> **and is indented at most three spaces**

SPEC.md, §11.7:

> the rest of a tab only partly consumed by indentation, which
> CommonMark keeps as spaces in the content.

conformance/cases/README.md, the table of leaf content:

> the block's lines, each ending in `\n`.
