# REFUSED(document-missing): the target does not exist

The link names `rules.md`, which is not in the current tree. Its pinned
blob is still readable.

SPEC.md §11.9:

> **The path** (0003, addendum, detail 7) is the destination's part before the
> `#` (CommonMark 0.31.2, *Links*), **as raw text**: character for character
> as the file writes it, with no backslash escape, entity reference or
> percent-encoding decoded. That is also the text a pin's `path` holds, and
> this definition governs both. So `my%20doc.md` names a file called
> `my%20doc.md`. It resolves relative to the directory that
> holds the referrer, as a renderer resolves a relative link, in the tree of
> the snapshot being resolved: it is split at `/`, a `.` segment is dropped,
> and a `..` segment removes the segment before it.
>
> - A path that begins with `/`, or whose first segment holds a `:`, is
>   absolute, and is `REFUSED(unresolvable-path)`.
> - A `..` that would go above the repository's root is
>   `REFUSED(unresolvable-path)`.
> - A path that names no file in that tree is `REFUSED(document-missing)`.
>   Names compare exactly, case included.

SPEC.md §11.9:

> **Resolution**, against the target's current text. A name **binds** only
> through a region marker (§7.2, §7.3); a heading slug never binds (0003,
> second addendum of 2026-10-16, item 6).
>
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
> 2. **The name** resolves as §8.1 says, against markers only. No match is
>    `#REF!(name)`. There is never more than one: step 1 requires the current
>    target to pass the profile, which refuses a name declared twice (§7.4;
>    same addendum, item 9).
> 3. For each text-bearing leaf the name binds in the pinned blob, §11.3 and
>    §11.4 run with that blob as `base`. A refusal, or no pair, refuses the
>    transclusion, as `REFUSED(pinned-<reason>)`, where `<reason>` is §11.4's
>    reason or `orphaned`. Where several leaves refuse, the first in the
>    pinned blob's document order is reported.
> 4. Each pair must lie inside what the name binds now. Otherwise the
>    transclusion is `REFUSED(name-rebound)`.
