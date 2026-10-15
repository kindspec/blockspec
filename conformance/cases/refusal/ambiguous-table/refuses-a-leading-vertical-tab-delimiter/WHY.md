0002, Addendum (ambiguous tables), as decided on 2026-10-15: "A form feed
or a vertical tab in either line refuses them. If either line holds one,
and the delimiter line holds nothing but `|`, `:`, `-`, spaces, tabs, form
feeds and vertical tabs, with at least one `-`, the lines are
`ambiguous-table`, whatever the header line holds."
The delimiter line is a vertical tab and `---`. pandoc 3.1.11.1 (`-f gfm`) and markdown-it-py 3.0.0 read one paragraph;
the profile refuses on purpose.
