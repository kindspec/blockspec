0001, Addendum (heading slugs): "the heading's content is lower-cased,
every character other than a letter, a mark, a number, `-`, `_` or a space
is removed, and each space becomes `-`. Every heading has a slug, at any
depth. No `-1` suffix is added to tell duplicates apart".
Each space becomes `-` and nothing collapses the run, so `pros - cons`
becomes `pros---cons`, and `pros-cons` names nothing.
