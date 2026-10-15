0002, Addendum (ambiguous tables), as decided on 2026-10-15: "A form feed
or a vertical tab in either line refuses them. If either line holds one,
and the delimiter line holds nothing but `|`, `:`, `-`, spaces, tabs, form
feeds and vertical tabs, with at least one `-`, the lines are
`ambiguous-table`, whatever the header line holds. Renderers disagree on
these characters in a table. The profile does not model any one of them,
and refuses the lot, which is lossless to relax."
Here the form feed is in the header line `a|`, and the delimiter line
`---|` is plain. pandoc 3.1.11.1 (`-f gfm`) and markdown-it-py 3.0.0 both
read a one-cell table whose cell keeps the form feed: the readers agree,
and the profile refuses on purpose.
