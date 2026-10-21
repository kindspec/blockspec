# anchor/transclusion/resolves-with-a-raw-ufffd-in-its-pin-line

The repository holds `doc.md`, the referrer, and the target `p`, U+FFFD,
`.md` (a file name holding U+FFFD, UTF-8 bytes EF BF BD), whose bytes are
`b'<!-- #scram -->\nThe scram threshold is 4.2 sigma.\n'`: the marker `scram` binding the paragraph `[1]`. `doc.md` has
frontmatter on lines 1 to 4 holding `pins:` and one pin line whose `blob` is
the target's current blob, then on line 6 the one transclusion paragraph
`[Scram](p?.md#scram "transclude")`, where `?` is the byte(s) noted below.

Here the pin line's `path` and the destination each hold a raw U+FFFD. This
is the accepting twin of `anchor/transclusion/refused-for-a-raw-u0000-in-its-pin-line`.

Expected: one transclusion, `[0]`, `RESOLVED`, unit `{"document": "p\ufffd.md",
"target": {"node": [1], "type": "paragraph"}}`.

§11.9, *The path*: "the destination's part before the `#` [...] **as raw
text**", and "A transclusion uses the pin whose `path` is equal to its own."
The pin's `path` is `p`, U+FFFD, `.md` written as itself, which is its
canonical form (§11.1, *Strings*). The steps of §11.9: the referrer passes
the profile (step 0); the path resolves, the pins follow the grammar, the
target exists and passes the profile (step 1.1 to 1.4); a marker binds
`scram` (1.5, step 2); the pinned blob is the current target, readable,
passing the profile and binding the name (1.6 to 1.8); its one text-bearing
leaf pairs `EXACT` with itself, with no other leaf to refuse it (step 3);
and the pair lies inside what the name binds now (step 4).

Files read (sha256, as computed before writing):
- SPEC.md 9635b4a43bff3d7d16497e8cbfae7863d65597ac9941aa9769a634fa14537a09
- cases-README.md ccc2999df3d77cfaea2a1340475cd38fc1261bd8d63262d20dc6a1018c284289
- case-body.schema.json 9512b41c957f0acae91c2ae84e7b1948e574bc06ea600e039991605152b3dcc8
- CASE-TREE.md ae9ef062966f380ebdbcdf3223d2d1d8f9ca5e294bc199166ce3c755493e7a8d
- CommonMark 0.31.2 spec.txt, from `npm pack commonmark-spec@0.31.2`
