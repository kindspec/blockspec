0002, Addendum (ambiguous tables), as decided on 2026-10-15: "A form feed
or a vertical tab in either line refuses them. If either line holds one,
and the delimiter line holds nothing but `|`, `:`, `-`, spaces, tabs, form
feeds and vertical tabs, with at least one `-`, the lines are
`ambiguous-table`, whatever the header line holds. Renderers disagree on
these characters in a table. The profile does not model any one of them,
and refuses the lot, which is lossless to relax."
The addendum also says the two lines are judged "without the line above
them", and "If the two lines alone are `ambiguous-table`, so is the
document, which takes precedence over `table-not-blank-above`." So `Two.`
over `---` and a form feed is refused, whatever the paragraph holds above
it. pandoc 3.1.11.1 (`-f gfm`) and markdown-it-py 3.0.0 read one
paragraph; the refusal is deliberate.
