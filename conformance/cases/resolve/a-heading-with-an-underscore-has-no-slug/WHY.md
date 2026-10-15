0001, Addendum (heading slugs): "The heading's raw content is lower-cased,
every character in the character class of github-slugger 2.0.0's
`regex.js` is removed, and each space becomes `-`." Every heading has a
slug, at any depth, except one whose raw content holds `*`, `_`, a
backtick, `[`, `<` or `&`, and no `-1` suffix tells duplicates apart.
`# snake_case` holds `_`, so it has no slug. The schema's name pattern,
`^[a-z0-9][a-z0-9-]*$`, cannot express `snake_case`, so this case cannot
ask for that name directly. It pins instead that neither `snakecase` nor
`snake-case`, the slugs a reader would get by dropping `_` or turning it
into `-`, resolves, while `kebab-case`, which keeps its `-`, resolves to
the second heading. The case was first named `resolve/slug-keeps-underscore`
and renamed when the no-slug rule made that name wrong; its expectations
did not change.
