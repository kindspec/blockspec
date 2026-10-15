0001, Addendum (heading slugs): "The heading's raw content is lower-cased,
every character in the character class of github-slugger 2.0.0's
`regex.js` is removed, and each space becomes `-`." Every heading has a
slug, at any depth, except one whose raw content holds `*`, `_`, a
backtick, `[`, `<` or `&`, and no `-1` suffix tells duplicates apart.
Both headings have the slug `usage`, the nested one included, so the name
matches two targets and is `#REF!(usage)` (0001, What draft 0 carries). A
reader that gave only top-level headings a slug would resolve it.
