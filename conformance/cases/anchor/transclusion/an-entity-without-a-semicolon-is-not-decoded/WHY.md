# No transclusion: a title of `&#116ransclude`

`&#116` without a `;` is not a numeric character reference in CommonMark
0.31.2, so the title is the literal text `&#116ransclude`, not
`transclude`.

SPEC.md §11.9:

> **A transclusion is a paragraph whose content is exactly one inline link
> with the title `transclude`** (0003 Q5)

CommonMark 0.31.2, *Entity and numeric character references*:

> [Decimal numeric character
> references](@)
> consist of `&#` + a string of 1--7 arabic digits + `;`.
