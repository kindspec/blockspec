0001, Addendum (heading slugs, as rewritten): slugs follow github-slugger
2.0.0 applied to the heading's raw content, and "a heading whose raw
content holds an inline-markup character, one of `*`, `_`, `` ` ``, `[` or
`<`, has no slug ... and a reference to it is unresolved, `#REF!(name)`".
Control for resolve/a-heading-with-inline-markup-has-no-slug: the plain
heading `em` has the slug `em`. The marked-up heading has none, so `em`
matches one target, not two. A reader that slugged `*em*` as `em` would
find two targets and return `#REF!(em)`.
