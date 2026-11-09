# An indented code block that only the merge produces

In the base and in each branch the four-space line sits inside a fence, as
code, and each branch alone is accepted. Ours deletes the outer opening fence,
theirs the inner opening fence, with `x` unchanged between. In the merged text
no fence encloses it, and it is an indented code block.

SPEC.md §9:

> 2. `indented-code`: an indented code block, at any depth, a marker line
>    indented four or more columns where a block can start included (§4.1,
>    §7.1)
