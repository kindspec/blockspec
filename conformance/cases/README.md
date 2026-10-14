<!-- SPDX-License-Identifier: CC0-1.0 -->
# The fixture tree

CC0. Copy it into any implementation, in any language. Everything a runner
needs is in the files.

This tree was written before any blockspec implementation existed. It encodes
draft 0 as `docs/adjudications/0001-syntax.md` and `0002-block.md` state it
(each section's *What draft 0 carries*). There is no `SPEC.md` yet. Where the
two adjudications leave a question open, the case's `WHY.md` says
**READING**, and the readings are listed below. A failing case is a finding,
not a bug in the case. **Add, do not edit**: changing a case to match an
implementation is how a suite stops measuring anything.

## Provenance

Written against blockspec `73f6567`, where no commit on any branch holds an
implementation (`git log --all -- reference/` prints nothing). The author had
the brief, the two adjudications, the org contract, kindkit `6ebd80d`
(`case-tree/`, its runner and its validator), and rowspec's
`conformance/cases/` with its README. Every fixture was written for this tree;
none is taken from a corpus.

## Shape

The tree follows kindkit's case-tree convention (kindspec/kindkit
`case-tree/CASE-TREE.md`):

    cases/<group>/<case-name>/
        expect.json     what to assert  (required; its presence IS the case)
        input.md        the document under test, exact bytes
        WHY.md          prose, ignored by the runner

    cases/refusal/<refusal-code>/<case-name>/
        the refusal cases for one code, and their controls

`case-body.schema.json` declares the shape of every `expect.json`. kindkit's
`tools/validate_case_tree.py` applies it.

## The one kind: `parse`

Every case has `"kind": "parse"`. The implementation reads `input.md` and
either refuses it or returns its structure.

| field | when | what it asserts |
| --- | --- | --- |
| `accept` | always | `true`: the document is in the profile. `false`: it is refused |
| `refusal` | `accept` is `false` | the one refusal that applies, by code (below) |
| `controls` | `accept` is `false` | ids of accepting cases on the other side of the line this refusal draws. Not an assertion about the implementation; `check_tree.py` checks they exist and accept |
| `blocks` | `accept` is `true` | every block, in order: `type` and `lines` |
| `leaves` | `accept` is `true` | every leaf, in document order: `node`, `type` and `content` |
| `names` | `accept` is `true` | every name a marker declares, and what it binds to. `{}` when there are none |
| `resolve` | optional | names to look up, and what each resolves to |

All of `blocks`, `leaves` and `names` are compared whole: a missing or extra
entry fails the case. `resolve` is compared for the names it lists.

### Blocks

A block is a top-level node (0002, *Decision*). `type` is one of
`paragraph`, `heading`, `code_block`, `html_block`, `thematic_break`,
`table`, `list`, `block_quote`. `lines` is `[first, last]`, 1-based and
inclusive. A block's range starts and ends on a non-blank line; blank lines
between blocks are in no block, and every non-blank line is in exactly one.

### Nodes and paths

A node is addressed by its path from the document: `[i]` is the i-th block,
and each further index is a child of the node before it, counting from 0. A
`list`'s children are its `list_item`s. A `list_item`'s and a `block_quote`'s
children are the nodes inside it, markers included. So `[2, 1, 0]` is the
first node of the second item of the list that is the third block.

A node in `names` or `resolve` is `{"node": path, "type": type}`, where
`type` may also be `list_item`. A region is `{"region": [node, ...]}`.

### Leaves and their content

A leaf is a `paragraph`, `heading`, `code_block`, `html_block`,
`thematic_break` or `table`, at any depth (0002, *What a leaf is*). Its
`content` is its parsed content, with container prefixes removed: list-item
indentation, `>` markers, and lazy continuation handled as CommonMark 0.31.2
defines it. Inline content is opaque, so inline markup is kept as written.

| type | content |
| --- | --- |
| `paragraph` | CommonMark's raw content (§4.8): the lines, each with its initial spaces or tabs removed, joined by `\n`, with final spaces or tabs removed |
| `heading` | the ATX heading's raw content (§4.2): without the opening `#` run, an optional closing `#` run, and the spaces around them |
| `code_block` | the lines between the fences, each ending in `\n`, with the fence's indentation removed. The info string is not content |
| `html_block` | the block's lines, each ending in `\n`. Under the profile, always one marker line |
| `thematic_break` | `""` |
| `table` | rows of cells, header row first, each cell's raw inline text trimmed. The delimiter row is not content |

### Names and resolution

`<!-- #name -->` binds `name` to the next sibling node in its container.
`<!-- #name:begin -->` and `<!-- #name:end -->` bind `name` to the sibling
nodes between them (0001, 0002 §3).

`resolve` tries a name against markers first, then heading slugs (0001). A
name that matches zero targets, or more than one, resolves to the string
`#REF!(name)`.

## Refusal codes

Each refusal case asserts exactly one code, and is written so that only one
refusal applies to it. An implementation may word its message however it
likes; the code is what the case compares.

| code | from | refused |
| --- | --- | --- |
| `setext-heading` | 0001 | a setext heading |
| `indented-code` | 0001 | an indented code block, at any depth |
| `link-reference-definition` | 0001 | a link reference definition, at any depth |
| `raw-html` | 0001 | an HTML block that is not a region marker |
| `duplicate-name` | 0001 | one name declared twice in one document |
| `conflict-marker` | 0001 | a git conflict-marker line |
| `dangling-marker` | 0002 §3 | a one-line marker with no next sibling in its container |
| `unpaired-region` | 0002 §3 | a `:begin` and its `:end` that are not siblings in one container |
| `table-not-blank-above` | 0002 §6 | a table with a non-blank line directly above it in its container |
| `table-not-blank-below` | 0002 §6 | a table with a non-blank line directly below it in its container |

## Readings

Each is marked READING in the `WHY.md` of the case that pins it.

1. **A region holds every sibling node between its markers, other markers
   included.** 0002 makes no exception for markers. `region/nested-pairs`,
   `region/overlapping-pairs`, `region/one-line-marker-inside-a-region`.
2. **A table needs a blank line or its container's edge on both sides,
   whatever the neighbouring line is.** 0002 states the rule both as two
   shapes (a paragraph line above, a non-blank line below) and in general
   ("on both sides"), and the brief states it in general. The general
   reading is the narrower profile, and relaxing it later is lossless. So a
   heading or a marker directly above a table is refused.
   `refusal/table-not-blank-above/refuses-a-heading-line-above`,
   `refuses-a-marker-directly-above`.
3. **A `:begin` with no `:end`, or an `:end` with no `:begin`, is
   `unpaired-region`.** 0002 refuses a pair across containers. An unmatched
   marker breaks the same rule: its partner is not a sibling in its container.
   `refusal/unpaired-region/refuses-a-begin-with-no-end`,
   `refuses-an-end-with-no-begin`.
4. **Conflict markers are refused even inside a fenced code block.** 0001 §4
   describes the refusal as "a line scan before any block parsing".
   `refusal/conflict-marker/refuses-inside-a-fence`.
5. **An HTML comment that is not a marker is raw HTML, and is refused.**
   `refusal/raw-html/refuses-an-ordinary-comment`.
6. **The raw-HTML refusal is block-level.** Inline HTML is opaque inline
   content. `refusal/raw-html/accepts-inline-html`.
7. **Slugs are tested only where every slug algorithm agrees.** Draft 0 names
   no slug algorithm, so the `resolve/` cases use headings whose text is one
   lower-case ASCII word.
8. **Leaf content, as tabled above.** 0002 says "parsed content, with
   container prefixes removed". The table pins what that is per type: a
   paragraph's and a heading's raw inline text, a code or HTML block's lines,
   and a table's cells.

## Not pinned yet

Questions the adjudications leave open, with no case in this tree, because
any case would decide them:

- **A marker whose next sibling is another marker.** "The next sibling node"
  is that marker. Whether two stacked names should both reach the node after
  them (an alias, which a rename would want), bind to the marker, or be
  refused is a design choice.
- **An empty region**, a `:begin` directly followed by its `:end`.
- **Frontmatter.** 0002 counts lines "after frontmatter", but neither
  adjudication admits it. Read literally, a YAML block's closing `---` is a
  setext underline and is refused.
- **The marker name grammar.** This tree only uses names matching D8's
  pattern, `[a-z0-9][a-z0-9-]*`, and never tests a name outside it.
- **CRLF line endings**, and which line ending a code block's content uses.
- **The slug algorithm**, and whether a heading inside a container has one.

## Running it

`conformance/check_tree.py` checks the tree itself and needs nothing else: the
floor, that each case can fail, and that each refusal has a control. Its
docstring lists what it checks.

`conformance/run_cases.py` runs the tree against an implementation, through
kindkit's runner. **With no implementation it reports no verdict (exit 2),
never a pass.** Its docstring gives the interface and the command.

kindkit's validator checks the tree against the case-tree convention and
`case-body.schema.json`:

    python3 <kindkit>/tools/validate_case_tree.py conformance/cases
