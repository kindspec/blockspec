# resolve/a-u0000-in-a-heading-is-in-no-slug

`input.md` is the one line `# a`, U+0000, `b`, then a line feed.

Accepted: one `heading` block on line 1. Its content is `a`, U+FFFD, `b`, and
the name `ab` resolves to it.

SPEC.md §3:

> **U+0000 is replaced with U+FFFD**, as the pinned grammar requires
> (CommonMark 0.31.2 §2.3, "Insecure characters").

SPEC.md §8.2:

> The class is github-slugger's own, not a Unicode category rule: it removes
> `²` and U+FFFD, and keeps `‿`, `Ⓐ`, `-` and `_`. Since §3 replaces
> U+0000 with U+FFFD, a U+0000 in a heading is in no slug: `a`, U+0000,
> `b` slugs to `ab`.

SPEC.md §8.1:

> **A name is tried against region markers first, then heading slugs**

and "the suite resolves a slug to the heading node (§12)". There is no
marker, and one heading has the slug `ab`, so `ab` resolves to `[0]`.

The content's U+FFFD comes from cases-README.md, *Leaves and their content*:
"A U+0000 in the file is U+FFFD in the content (`SPEC.md` §3)." None of
`*`, `_`, a backtick, `[`, `<` or `&` is in the heading, so it has a slug.

Files read (sha256, as computed before writing):
- SPEC.md 9635b4a43bff3d7d16497e8cbfae7863d65597ac9941aa9769a634fa14537a09
- cases-README.md ccc2999df3d77cfaea2a1340475cd38fc1261bd8d63262d20dc6a1018c284289
- case-body.schema.json 9512b41c957f0acae91c2ae84e7b1948e574bc06ea600e039991605152b3dcc8
- CASE-TREE.md ae9ef062966f380ebdbcdf3223d2d1d8f9ca5e294bc199166ce3c755493e7a8d
- CommonMark 0.31.2 spec.txt, from `npm pack commonmark-spec@0.31.2`
