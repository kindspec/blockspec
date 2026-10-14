READING: a table leaf's content is its cells as GFM's table extension defines
them. `\|` inside a cell is an escaped pipe and the cell holds `|`; a body row
shorter than the header row is padded with empty cells, and cells past the
header's width are dropped. markdown-it and pandoc's gfm reader agree on all
three.
