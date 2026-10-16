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

> **Resolution**, against the target's current text:
>
> 0. The path must resolve, or `REFUSED(unresolvable-path)`. The target
>    document must exist, or `REFUSED(document-missing)`, and the
>    pinned blob must be readable, or `REFUSED(base-unavailable)`. Both the
>    pinned blob and the current target must pass the profile, or
>    `REFUSED(not-in-profile)`. The name must bind in the pinned blob, or
>    `REFUSED(record-inconsistent)`.
> 1. The name resolves as §8.1 says, against markers only. Zero matches, or
>    more than one, is `#REF!(name)`.
> 2. For each text-bearing leaf the name bound in the pinned blob, §11.3 and
>    §11.4 run with that blob as `base`. A refusal, or no pair, refuses the
>    transclusion, as `REFUSED(pinned-<reason>)`, where `<reason>` is §11.4's
>    reason or `orphaned`.
> 3. Each pair must lie inside what the name binds now. Otherwise the
>    transclusion is `REFUSED(name-rebound)`.
