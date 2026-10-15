CommonMark 0.31.2 §5.2, rule 1: a list marker of width W followed by N
spaces of indentation (1 <= N <= 4) puts the item's later lines at W + N.
Here W + N is 1 + 3 = 4, so `two`, indented 2 after a blank line, is not
in the item, and the list ends. The spec's examples after rule 1
(`- one` / blank / ` two`, and ` -    one` / blank / `     two`) show the
same arithmetic.
pandoc 3.1.11.1 (`-f commonmark`) agrees. markdown-it-py 3.0.0
(`commonmark` preset) puts `two` in the item, against the spec's own
examples, so it is not a safe second opinion for this shape.
