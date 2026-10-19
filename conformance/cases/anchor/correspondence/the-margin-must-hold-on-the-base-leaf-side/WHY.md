# ORPHANED: two light edits of one paragraph, neither leading

The anchored paragraph's gap now holds two current leaves, each a light
edit of it: one changes its last clause (`L = 200`, `T = 413`), the other
its first words (`L = 202`, `T = 406`). Neither similarity exceeds the
other by 0.15, so the anchored leaf's own margin fails against both, and it
pairs with neither. Each current leaf has only one leftover base leaf to
compare with, so a resolver that checked only the current leaf's side
would pair one of them and report `REFUSED(crowded-gap)`. No current leaf
is a copy, so the anchor is `ORPHANED`.

SPEC.md §11.3:

> 3. **Edits.** A base leaf `i` and a current leaf `j` left over in the same
>    gap pair as `EDITED` when all of these hold: their similarity is at least
>    0.5; it exceeds the similarity of `i` to every other leftover current
>    leaf in the gap by at least 0.15; and it exceeds the similarity of `j` to
>    every other leftover base leaf in the gap by at least 0.15.

SPEC.md §11.3:

> | §11 states | compare |
> | --- | --- |
> | similarity at least 0.5 | `4·L ≥ T` |
> | similarity at least 0.3 | `20·L ≥ 3·T` |
> | similarity below 1 | `2·L < T` |
> | `2·L₁/T₁` exceeds `2·L₂/T₂` by at least 0.15 | `40·L₁·T₂ − 40·L₂·T₁ ≥ 3·T₁·T₂` |
