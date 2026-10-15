0001, Addendum (heading slugs, as rewritten): slugs follow github-slugger
2.0.0 applied to the heading's raw content, and "a heading whose raw
content holds an inline-markup character, one of `*`, `_`, `` ` ``, `[` or
`<`, has no slug ... and a reference to it is unresolved, `#REF!(name)`".
`*em*` holds `*`, so the heading has no slug, and `em`, the slug GitHub
gives the rendered heading, names nothing.
