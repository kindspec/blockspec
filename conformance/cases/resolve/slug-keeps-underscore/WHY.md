0001, Addendum (heading slugs): "The heading's raw content is lower-cased,
every character in the character class of github-slugger 2.0.0's
`regex.js` is removed, and each space becomes `-`." Every heading has a
slug, at any depth, except one whose raw content holds `*`, `_`, a
backtick, `[` or `<`, and no `-1` suffix tells duplicates apart.
Since the addendum was rewritten, a heading whose raw content holds `_` has
no slug at all, so `snake_case` names nothing, and neither does `snakecase`
or `snake-case`, the slugs a reader would get by dropping `_` or turning it
into `-`. `kebab-case` keeps its `-` and resolves to the second heading.
(The case's expectations were written before the rewrite and still hold.)
