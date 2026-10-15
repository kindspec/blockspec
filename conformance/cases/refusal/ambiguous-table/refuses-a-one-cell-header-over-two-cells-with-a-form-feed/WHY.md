0002, Addendum (ambiguous tables), as decided on 2026-10-15: "A form feed
or a vertical tab in either line refuses them. If either line holds one,
and the delimiter line holds nothing but `|`, `:`, `-`, spaces, tabs, form
feeds and vertical tabs, with at least one `-`, the lines are
`ambiguous-table`, whatever the header line holds. Renderers disagree on
these characters in a table. The profile does not model any one of them,
and refuses the lot, which is lossless to relax."
The delimiter line `--- | ---` and a form feed holds only those
characters and a `-`, so the lines are refused whatever the header holds,
even though the header has one cell against two. pandoc 3.1.11.1
(`-f gfm`) and markdown-it-py 3.0.0 read one paragraph; the refusal is
deliberate, not a reader disagreement. This case was first an accepting
control, `refusal/ambiguous-table/accepts-a-one-cell-header-over-two-cells-with-a-form-feed`,
under the addendum's earlier wording, which counted cells first; it moved
here when the rewrite made form feeds refuse on sight.
