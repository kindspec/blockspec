# MOVED and RESOLVED: two paragraphs swap places

`base` holds the heading, paragraph `I` and paragraph `B`; the current
text the heading, `B` and `I`. Numbering the current text-bearing leaves
0 to 2, the unique pairs in base order have current indices 0, 2, 1. Two
chains are longest, `0, 2` and `0, 1`, and the leftmost is `0, 1`: the
heading and `B`, the leaf now first. So the comment on `B` is `RESOLVED`
and the comment on `I` is `MOVED`. A tie-break in base order would make
`I` `EXACT` instead.

SPEC.md §11.3:

> **When several subsequences are longest, the chain is the
>    leftmost** (0003, addendum, detail 4): number the current text-bearing
>    leaves from 0 in document order; the chain is the one whose sequence of
>    current indices, in base order, is lexicographically smallest, so at the
>    first position where two differ, the smaller index wins.

0003, addendum, detail 4:

> For two unique leaves that swap
> places, both chains have length 1, and the chain is the pair of the leaf
> that is now first: it is `EXACT`, and the other is `MOVED`.
