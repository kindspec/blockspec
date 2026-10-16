# REFUSED(not-in-profile), as a whole: a referrer holding raw HTML

The referrer's body holds a `<div>` block, which the profile refuses. Its
one transclusion would otherwise resolve.

SPEC.md §11.9:

> 0. **The referrer.** A referrer the profile refuses is refused as a whole,
>    `REFUSED(not-in-profile)`, and its transclusions are not enumerated: a
>    refused file has no tree to find them in. A conflict-marker line
>    anywhere in it counts, in its frontmatter and in a fenced code block
>    alike, whatever readings 4 and 12 say (same addendum, item 7).
> 1. **The inputs**, checked in this order; the first that fails decides
>    (same addendum, items 2 and 3, with its precision):
>    1. the path must resolve, or `REFUSED(unresolvable-path)`;
>    2. the referrer's pins must follow the grammar above, or
>       `REFUSED(record-inconsistent)`;
>    3. the target document must exist, or `REFUSED(document-missing)`;
>    4. the current target must pass the profile, or
>       `REFUSED(not-in-profile)`;
>    5. a name that only a heading slug matches in the current target is
>       `#REF!(name)` (item 6). A marker name that is also some heading's
>       slug resolves to the marker (§8.1);
>    6. the pinned blob must be readable, or `REFUSED(base-unavailable)`;
>    7. the pinned blob must pass the profile, or `REFUSED(not-in-profile)`;
>    8. a marker must bind the name in the pinned blob, or
>       `REFUSED(record-inconsistent)`.

0003, second addendum, item 7:

> - **A referrer the profile refuses is refused as a whole**, as
>   `not-in-profile`, whatever the profile refuses it for, and its
>   transclusions are not enumerated: a refused file has no tree in which to
>   find a transclusion paragraph.
