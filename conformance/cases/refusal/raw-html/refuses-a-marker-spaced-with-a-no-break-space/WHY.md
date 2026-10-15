0001, Addendum (the marker line, as rewritten): a marker matches
`^[ \t]*<!--[ \t]*#[a-z0-9][a-z0-9-]*(:begin|:end)?[ \t]*-->[ \t]*$`.
"The only spacing allowed is spaces and tabs ... Other whitespace, such as
a no-break space, is not." "An HTML comment that does not match is raw
HTML, and is refused as raw HTML."
The space after `<!--` here is U+00A0, a no-break space (bytes C2 A0), so
the line is not a marker. It still opens a type 2 HTML block (CommonMark
0.31.2 §4.6), which is raw HTML. A regex `\s` matches U+00A0, so a reader
built on `\s` accepts this line.
