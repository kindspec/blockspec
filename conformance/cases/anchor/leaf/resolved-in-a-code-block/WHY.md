# RESOLVED: a span in a fenced code block

The anchor's `leaf.type` is `code`, and its text is the lines between the
fences, each ending in `\n`. Another paragraph was edited; the code block is
unchanged and stays on the chain.

SPEC.md §11.1:

> | `leaf.type` | `p`, `h1` to `h6`, `code` or `table`: a paragraph, a heading with its level, a code block or a table |

SPEC.md §11.2:

> The resolver works on each snapshot's **text-bearing leaves**, in document
> order: paragraphs, headings, code blocks and tables.
