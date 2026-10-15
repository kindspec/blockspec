Owner's ruling of 2026-10-14 (0001, Addendum, heading slugs): a heading
whose raw content holds an inline-markup character, one of `*`, `_`,
`` ` ``, `[`, `<` or `&`, has no slug, "because its raw content is not the
text GitHub slugs, and a reference to it is unresolved, `#REF!(name)`".
`Q&amp;A` holds that character, so `qampa`, the slug github-slugger
2.0.0 computes from the raw content, names nothing. The control
resolve/plain-heading-slug-for-the-ampersand-case gives a heading without the
character the same slug, and it resolves.
`qa` is the slug GitHub gives the rendered heading (`Q&A`); it names
nothing either, because the heading has no slug at all.
