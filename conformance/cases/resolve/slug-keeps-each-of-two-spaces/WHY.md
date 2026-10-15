0001, Addendum (heading slugs): "The heading's raw content is lower-cased,
every character in the character class of github-slugger 2.0.0's
`regex.js` is removed, and each space becomes `-`." CommonMark 0.31.2 §4.2 strips
only leading and trailing spaces from a heading's content, so the two
spaces inside `step  one` stay, and each becomes `-`: the slug is
`step--one`. A reader that collapsed runs of spaces would resolve
`step-one` instead, which names nothing here.
