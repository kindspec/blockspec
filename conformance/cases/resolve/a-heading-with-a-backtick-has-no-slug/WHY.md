0001, Addendum (heading slugs): "A heading whose raw content holds an
inline-markup character, one of `*`, `_`, `` ` ``, `[` or `<`, or an `&`,
which may begin an entity reference, has **no slug**. Its raw content is
not the text GitHub slugs, so a reference to it is unresolved,
`#REF!(name)`."
``code` x` holds that character, so `code-x`, the slug github-slugger
2.0.0 computes from the raw content, names nothing. The control
resolve/plain-heading-slug-for-the-backtick-case gives a heading without the
character the same slug, and it resolves.
