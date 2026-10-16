# RESOLVED: the named paragraph was edited

The pinned blob is older than the target's current text, whose named
paragraph gained two words at its end. Run against the pinned blob, the
paragraph pairs as `EDITED`, which no rule refuses, and its pair is what
the name binds now. 0003 §8: the anchored leaf edited, the transclusion
resolves.

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

0003 §7:

> Editing inside the named content passes step 3, so a target's
> author can usually revise the text without breaking its readers.
