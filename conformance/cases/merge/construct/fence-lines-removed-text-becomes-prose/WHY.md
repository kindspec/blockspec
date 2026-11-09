# Fence lines removed on each side turn code into prose

The control for the two preceding cases: the same deletion of two different
fence lines, with no construct the profile refuses in the middle. In the base
and on each branch, `Text line.` is a line of a code block. In the merged text,
`x` and `Text line.` are one paragraph, and the remaining two fence lines are
an empty code block. The merged file is accepted: a merge changed what is code
and what is prose, and no refusal applies.

This is one of the silently wrong merges reported with this set.

CommonMark 0.31.2 §4.5 lets a longer run close a fence. SPEC.md §6.2:

> **A leaf is a paragraph, heading, code block, HTML block, table or thematic
> break, at any depth** (0002, *What a leaf is*).
