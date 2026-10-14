READING: D8 §7.2 says git emits "7-or-more-character" marker runs at column 0
(a larger conflict-marker-size, or nested conflicts). A run of seven or more
`<`, `>` or `|` followed by a space or the end of the line is a marker line, so
eight is refused. Refusing more is the narrower profile; relaxing it later is
lossless.
