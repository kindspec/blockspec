0001, Addendum (the marker line): a marker is a line matching
`^[ \t]*<!--[ \t]*#[a-z0-9][a-z0-9-]*(:begin|:end)?[ \t]*-->[ \t]*$`, and "the only
spacing allowed is spaces and tabs, inside and around the comment". Each marker here varies it: none
inside (line 1), two spaces inside and trailing spaces after (line 4),
tabs inside a `:begin` (line 7), and two spaces of indentation (line 11).
An HTML block's content is its lines as written (CommonMark 0.31.2 §4.6
keeps the indentation and trailing spaces of a type 2 block), so the
spacing stays in each marker's content.
