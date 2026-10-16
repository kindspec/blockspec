# RESOLVED: a pinned target that has not changed

`guide.md` transcludes `policy.md#scram-threshold`, a one-line marker
naming the paragraph after it, and pins the target's current blob. The
unit is that paragraph, node `[2]` of `policy.md`.

SPEC.md §11.9:

> **A transclusion is a paragraph whose content is exactly one inline link
> with the title `transclude`** (0003 Q5)

SPEC.md §11.9:

> **The unit transcluded is what the name binds** (0002 §4): one node with
> its subtree, or the nodes of one region.

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
