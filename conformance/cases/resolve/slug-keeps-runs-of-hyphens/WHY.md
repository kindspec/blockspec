0001, Addendum (heading slugs): "The heading's raw content is lower-cased,
every character in the character class of github-slugger 2.0.0's
`regex.js` is removed, and each space becomes `-`." Every heading has a
slug, at any depth, except one whose raw content holds `*`, `_`, a
backtick, `[` or `<`, and no `-1` suffix tells duplicates apart.
Each space becomes `-` and nothing collapses the run, so `pros - cons`
becomes `pros---cons`, and `pros-cons` names nothing.
