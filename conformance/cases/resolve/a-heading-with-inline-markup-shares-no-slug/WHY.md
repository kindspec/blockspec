0001, Addendum (heading slugs): slugs follow github-slugger 2.0.0 applied
to the heading's raw content, and "A heading whose raw content holds an
inline-markup character, one of `*`, `_`, `` ` ``, `[` or `<`, or an `&`,
which may begin an entity reference, has **no slug**. Its raw content is
not the text GitHub slugs, so a reference to it is unresolved,
`#REF!(name)`."
Control for resolve/a-heading-with-inline-markup-has-no-slug: the plain
heading `em` has the slug `em`. The marked-up heading has none, so `em`
matches one target, not two. A reader that slugged `*em*` as `em` would
find two targets and return `#REF!(em)`.
