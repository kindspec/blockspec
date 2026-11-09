# A heading whose slug is not empty

Control: the punctuation goes and the space between becomes `-`, so the slug
is `-`, not empty. The empty name still matches nothing.

docs/adjudications/0005-closing-draft-0s-gaps.md, item 8:

> **8. A heading whose slug comes out empty has no slug**, as `# !!!`
> has none. A reference to it is `#REF!(name)`, and so is the empty
> name.

SPEC.md, §8.2:

> every character in the character class of github-slugger 2.0.0's
> `regex.js` is removed, and each space becomes `-`.
