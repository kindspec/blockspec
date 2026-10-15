0001, Addendum (heading slugs): slugs follow github-slugger 2.0.0 applied
to the heading's raw content, and "A heading whose raw content holds an
inline-markup character, one of `*`, `_`, `` ` ``, `[` or `<`, or an `&`,
which may begin an entity reference, has **no slug**. Its raw content is
not the text GitHub slugs, so a reference to it is unresolved,
`#REF!(name)`."
`*em*` holds `*`, so the heading has no slug, and `em`, the slug GitHub
gives the rendered heading, names nothing.
