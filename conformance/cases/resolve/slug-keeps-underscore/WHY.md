0001, Addendum (heading slugs): "the heading's content is lower-cased,
every character other than a letter, a mark, a number, `-`, `_` or a space
is removed, and each space becomes `-`. Every heading has a slug, at any
depth. No `-1` suffix is added to tell duplicates apart".
`_` and `-` are both kept. The first heading's slug is `snake_case`,
which no name in `resolve` can spell (the case schema's name pattern has no
`_`), so this case checks that neither of the slugs a reader would get by
dropping `_` or turning it into `-` resolves, while the second heading's
`kebab-case` does.
