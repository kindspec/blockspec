# A setext heading that only the merge produces

In the base the `Title` and `---` lines are inside a four-backtick fence, and
so in each branch, where they are inside a three- or four-backtick fence:
each branch alone is accepted. Ours deletes the outer opening fence and
theirs the inner opening fence, with `x` unchanged between. In the merged text
no fence opens above them, and `x`, `Title` and `---` read as a setext heading.

SPEC.md §9:

> 1. `setext-heading`: a setext heading, at any depth (§4.1)

SPEC.md §4.1:

> - a setext heading (`setext-heading`);
