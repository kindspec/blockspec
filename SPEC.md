<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# blockspec — specification, draft 0

Status: draft. This document writes up draft 0 as
`docs/adjudications/0001-syntax.md` and `0002-block.md` decide it, with
their addenda. It adds no decision of its own. **Where this document and an
adjudication disagree, the adjudication wins and this document is in
error.** Where the adjudications are silent, this document says so (§11)
instead of choosing.

The conformance suite, `conformance/cases/`, was written from the same
adjudications before any implementation existed. Where they left a question
open, a case takes a reading and its `WHY.md` says **READING**. A reading is
not a decision, and §11 lists each one.

**[CHOICE]** marks a decision that had a real alternative, with the reason
the adjudication gave for it.

---

## 1. What this format is for

A prose document that several people edit, in git, over years, where a merge
that is quietly wrong is worse than a merge that fails.

A blockspec document is a markdown file that renders and edits correctly in
today's markdown tools. It adds one convention, a region marker that lets an
author name a part of the document, and it refuses the markdown constructs on
which mature parsers draw different trees, or which hide what a merge did.

**A block gets no minted id.** Identity is computed from content where it can
be, and named by an author where it must be (`DESIGN-BRIEF.md` §1, with the
measurement behind it; D8's invariant I7). Nothing in this document requires
writing an identifier into the text.

## 2. What this document decides

Specified here, because two implementations that disagree on any of it read
the same file differently: the profile and its refusals (§4, §9), where
frontmatter ends (§5), how a document is cut into blocks and leaves (§6),
what each name binds to (§7), and how a name resolves (§8).

Not specified here: rendering, how a refusal is worded, editor behaviour,
and anything about inline content beyond keeping it as written (§4.2).

## 3. Encoding and lines

A document is UTF-8 text, one document per file (`DESIGN-BRIEF.md` §1).

Lines, line endings and tabs are CommonMark 0.31.2's (§2.1 and §2.2 of its
spec): a line ends at a line feed, a carriage return, or the pair, and a tab
advances to the next multiple of four columns wherever spaces define block
structure.

**Leaf content uses `\n` as its line ending everywhere**, code blocks
included, whatever line endings the file uses (0002, addendum on markers that
name nothing, and three defaults).

## 4. The profile

### 4.1 The base grammar

**A document is read as CommonMark 0.31.2, pinned by its tag `0.31.2`, at
block level only, with GFM pipe tables** (0001, *Decision* and *What draft 0
carries*; 0002 §6).

**[CHOICE]** markdown over djot. The deciding input was the owner's answer
that a blockspec document must render and edit correctly in today's markdown
tools, GitHub and other forge previews, Obsidian and ordinary editors (0001,
*The owner's answer*). 0001 §3 adds that CommonMark gives every implementer a
mature parser to diff against, and that 0.31.2 is stable.

The blocks the profile admits, at any depth:

| CommonMark construct | admitted as |
| --- | --- |
| ATX heading (§4.2) | leaf `heading` |
| fenced code block (§4.5) | leaf `code_block` |
| HTML block (§4.6) that is a region marker (§7.1) | leaf `html_block` |
| paragraph (§4.8) | leaf `paragraph` |
| thematic break (§4.1) | leaf `thematic_break` |
| GFM pipe table (§4.3 below) | leaf `table` |
| block quote (§5.1) | container `block_quote` |
| list (§5.3) of list items (§5.2) | container `list`, holding `list_item`s |

Refused, at any depth, each with the identifier in §9 (0001, *What draft 0
carries*):

- a setext heading (`setext-heading`);
- an indented code block (`indented-code`);
- a link reference definition (`link-reference-definition`);
- an HTML block that is not a region marker (`raw-html`). An HTML comment
  that does not match §7.1's marker line is raw HTML (0001, addendum).

**[CHOICE]** refuse these rather than read them. 0001 §3: the profile can
refuse setext headings, indented code, link reference definitions and raw
HTML other than the marker, which shrinks what an implementation must get
right. Refusing still needs detecting: a setext underline is recognised in
paragraph context, as CommonMark recognises it.

### 4.2 Inline content is opaque

The profile is block-level. **Inline content is opaque text** (0001, *What
draft 0 carries*): a leaf's inline content is kept as written and is not
parsed, so emphasis, links, code spans and entity references are characters
of the leaf's content (§6.3), not structure.

### 4.3 Tables

**GFM pipe tables are in the profile, as a leaf block**, from the GFM spec's
"Tables (extension)" section, version 0.29-gfm (0002 §6). A table in a
blockspec document is an opaque leaf: it has no row ids, no formulas and no
key. Tabular data that needs identity or computation belongs in a rowspec
file (0002 §6).

**[CHOICE]** admit tables rather than read them as paragraphs. GitHub and
Obsidian render pipe tables as tables, so a profile that read them as
paragraphs would build a different tree from the one every author sees (0002
§6).

**A table must have a blank line, or its container's edge, on both sides**
(0002, *Decision*). So:

- a table with a non-blank line directly above it in its container is
  refused (`table-not-blank-above`);
- a table with a non-blank line directly below it in its container is
  refused (`table-not-blank-below`). A non-blank line directly after a
  table's rows that markdown-it reads as one more row and pandoc as a
  paragraph is this refusal (0002, addendum on ambiguous tables);
- a row that is only `|`, with or without spaces around it, ends the table.
  The line is then a non-blank line directly below it, and is refused as
  `table-not-blank-below` (same addendum).

**The table start is tried after every core block start**, as cmark-gfm
tries its extensions. So `a | b` over `- | -` is a paragraph and a bullet
list, not a table (same addendum).

**Ambiguous tables.** A delimiter line and the paragraph line over it, in
the same container, are judged as two lines, **without the line above
them**, at top level, in a block quote or in a list item alike. The
delimiter line must not already be a setext underline, a thematic break or a
list item, which are tried first (0002, addendum on ambiguous tables):

1. If either line holds a form feed or a vertical tab, and the delimiter line
   holds nothing but `|`, `:`, `-`, spaces, tabs, form feeds and vertical
   tabs, with at least one `-`, the lines are refused as `ambiguous-table`,
   whatever the header line holds.
2. Otherwise the two lines are a **table candidate** when the delimiter row's
   cells, split on unescaped pipes and trimmed of spaces and tabs, are each
   `:?-+:?`, and the header line splits into as many cells. A candidate with
   no unescaped pipe in one of its two lines is refused as `ambiguous-table`.
   A candidate with a pipe in both lines is a table.
3. A lazy header line is read as it stands: whitespace before its leading
   pipe makes an empty first cell.

If the two lines alone are `ambiguous-table`, so is the document, and that
takes precedence over `table-not-blank-above`. If the two lines alone are a
table, a paragraph line above them makes it `table-not-blank-above`.

**[CHOICE]** refuse where mature parsers disagree. When two mature parsers
draw different trees, the profile refuses the input (0002 §6), which is
lossless to relax later.

### 4.4 Conflict markers

**A file holding a git conflict-marker line is refused** (`conflict-marker`),
as a line scan before any block parsing (0001 §4 and *What draft 0
carries*). Git's markers are column-0 runs of seven `<`, `=` or `>`, and of
seven `|` for diff3's base marker (0001 §4). Because the scan precedes
parsing, a marker line is refused wherever it sits.

**[CHOICE]** refuse, rather than leave the markers to the parser. Under
CommonMark a conflicted file parses without error: the first marker line
becomes heading text, `=======` disappears into a setext underline, and the
last becomes nested block quotes (0001, the factual disputes, and §4).

## 5. Frontmatter

**Frontmatter is allowed** (0002, addendum on frontmatter). A leading YAML
block is opaque metadata. It is not a block, has no leaves and takes no
names. Its lines are in no block.

- **It opens with a line that is exactly `---`, on line 1.**
- **Line 2 must not be blank**, as pandoc reads a YAML metadata block. A
  document whose line 1 is `---` and whose line 2 is blank opens with a
  thematic break, whatever `---` lines come later.
- **It is closed by a line of `---` followed only by spaces or tabs**, and
  never by YAML's `...` document end marker (0002, addendum on markers that
  name nothing, and three defaults).

Without frontmatter, a YAML block's opening `---` would be a thematic break
and its closing `---` a setext underline, which §4.1 refuses (0002, addendum
on frontmatter).

## 6. Blocks and leaves

"Block" is one thing, the unit the document is cut into. Each other job the
word did addresses a node of the same tree, and each gets the node 0002's
evidence picked for it (0002, *Decision*).

### 6.1 Blocks: the partition

**A block is a top-level node.** A document is a sequence of blocks. A list
is one block, and so are a block quote and a table. **Every non-blank line
after frontmatter is in exactly one block** (0002 §1).

**[CHOICE]** the top-level node over the leaf as the partition. Only a
top-level node partitions the lines: list markers and `>` prefixes belong to
no leaf. Of the definitions that cover every node type, it also duplicates
least within a file (0002 §1).

Consequences that are CommonMark's, not the profile's, and that the suite
pins (0002 §5): a change of bullet character, or of an ordered list's
delimiter, splits a list into two blocks, and so does a marker at column 0
between two items (0002 §3). One blank line between any two items makes the
whole list loose, and it is still one block.

### 6.2 Leaves

**A leaf is a paragraph, heading, code block, HTML block, table or thematic
break, at any depth** (0002, *What a leaf is*). Under the profile an HTML
block is always a region marker and a code block is always fenced. A marker
and a thematic break carry no text, so an anchor lands in a paragraph,
heading, fenced code block or table.

**Stage 1 of every anchor resolves a leaf**, with no fallback to the
enclosing block (0002 §2). The anchor format is not part of draft 0.

**[CHOICE]** the leaf, not the block, for anchoring. Graded against D8's
line oracle, the leaf was correct at least as often as the enclosing item,
and the item at least as often as the block, in every arm and gap measured,
and the only silent wrong of the run came from the coarse scope (0002 §2).

### 6.3 Leaf content

**A leaf's content is its parsed content, as CommonMark parses it, with
container prefixes removed**: list-item indentation, `>` markers, and lazy
continuation handled as CommonMark 0.31.2 defines a paragraph's content
(0002 §2 and *What draft 0 carries*). 0001 §6 asks for anchors to quote this
parsed text rather than raw bytes, so the blocks are raw lines and the
anchors are parsed text, each for its own job. Line endings in content are
`\n` (§3).

What that is per leaf type is the suite's reading (§11, reading 8).

## 7. Names

### 7.1 The marker line

An author names part of a document with a **region marker**, D8 §7.2's
convention (kindspec/research `design-findings/D8-identity.md`), and the
only convention the profile adds (0001, *What draft 0 carries*). It has two
forms: `<!-- #name -->` on its own line, and the pair `<!-- #name:begin -->`
and `<!-- #name:end -->`.

**A region marker is a line whose content, after any container prefix,
matches**

    ^[ \t]*<!--[ \t]*#[a-z0-9][a-z0-9-]*(:begin|:end)?[ \t]*-->[ \t]*$

**and is indented at most three spaces** (0001, addendum). Four or more make
the line an indented code block, which §4.1 refuses. The only spacing allowed
is spaces and tabs, inside and around the comment, so `<!--#intro-->` and
`<!--  #intro  -->` are both markers, and a no-break space is not spacing.
Nothing else may share the line. An HTML comment that does not match is raw
HTML, refused as `raw-html`.

A marker is an HTML block of CommonMark type 2, so it may interrupt a
paragraph: a marker on the line after a paragraph line still names the next
node (0001, the factual disputes).

**[CHOICE]** an HTML comment as the carrier. It is invisible in every
renderer, GitHub's included, where an attribute such as `{#custom-id}`
renders as visible text under CommonMark (0001 §1, citing D8 §7.2).

### 7.2 What a one-line marker names

**`<!-- #name -->` binds `name` to the next sibling node in its container**,
at any depth (0001; 0002 §3). At top level that node is a block; inside a
list item or a block quote it is the next node there. A blank line between
the marker and the node does not matter.

**A marker must name a node** (0002, addendum on markers that name nothing).
These are refused as `dangling-marker`:

- a one-line marker with no next sibling in its container;
- a one-line marker whose next sibling is another marker. A name binds to
  content, never to a marker, so stacking two markers does not make an
  alias;
- an empty region (§7.3).

A list item is the one node a one-line marker cannot name: the marker would
have to sit between items, and there it ends the list. That is a CommonMark
fact, not a profile choice. A region pair inside the item names
its content (0002 §3).

### 7.3 Regions

**A `:begin` / `:end` pair binds `name` to the sibling nodes between its two
markers.** Both markers must be siblings in one container, or the pair is
refused as `unpaired-region` (0002 §3). A region may nest inside, or overlap,
another (0001, *What draft 0 carries*). A `:begin` directly followed by its
`:end`, with no node between them, is an empty region, refused as
`dangling-marker` (§7.2).

**[CHOICE]** both markers in one container. It is a narrowing, and relaxing
it later is lossless, because every region valid under it stays valid (0002
§3).

### 7.4 Duplicate names

**A name declared twice in one document is refused** (`duplicate-name`;
0001, *What draft 0 carries*). A name is declared by a one-line marker or by
a `:begin`. An `:end` closes a region and declares nothing (0002, addendum on
markers that name nothing).

## 8. Resolution

### 8.1 Order

**A name is tried against region markers first, then heading slugs**, per D8
§7.2's order (0001, *What draft 0 carries*). **A name that matches zero
targets, or more than one, is `#REF!(name)`.** A marker's name never matches
more than one target, since a duplicate is refused (§7.4), so a marker name
resolves even where two headings share it as a slug.

What a name resolves to is the node a marker binds (§7.2), the nodes of a
region (§7.3), or the heading whose slug it is.

### 8.2 Heading slugs

**Heading slugs follow GitHub's rule, character for character as
github-slugger 2.0.0 computes it** (0001, addendum). A heading's raw content
(CommonMark §4.2: without the opening `#` run, an optional closing `#` run,
and the spaces around them) is lower-cased, every character in the character
class of github-slugger 2.0.0's `regex.js` is removed, and each space becomes
`-`.

- The class is github-slugger's own, not a Unicode category rule: it removes
  `²`, and keeps `‿`, `Ⓐ`, `-` and `_`. `tools/slugger/` generates the
  reference's copy of the class and checks it against the original.
- Lower-casing is the reader's runtime's own, so it follows that runtime's
  Unicode version: U+A7CB and U+A7DC lower-case under node 24 (Unicode 17)
  and not under Python 3.11 to 3.13.
- **Every heading has a slug, at any depth, with one exception**: a heading
  whose raw content holds `*`, `_`, `` ` ``, `[`, `<` or `&` has no slug. Its
  raw content is not the text GitHub slugs, so a reference to it is
  `#REF!(name)`.
- **No `-1` suffix** tells duplicates apart, so two headings with one slug
  leave that slug unresolved (§8.1).

A slug may hold characters that §7.1's name grammar does not, since it comes
from the heading's text.

### 8.3 Slugs are resolvable, not durable

**A heading slug is a convenience, not a reference blockspec promises to
keep** (0001, *What draft 0 carries*).

**[CHOICE]** keep slugs resolvable but not durable. Of the 432 qualifying
units summed over the spike's FOUND cells, 265 are name references (R), every
R record in its reproduction is a heading slug, and in 171 of the 265 the
oracle says the target was deleted and the slug resolved to something else
(0001, the factual disputes, and §2).
The remedy is not to treat derived names as durable references, and that is
available in either syntax (0001 §2).

## 9. Refusals — normative

A document is either accepted, with the structure §5–§8 describe, or refused.
**This list is complete**: every refusal draft 0 has is below, with the
identifier the conformance suite compares. An implementation reports the
identifier of the refusal it applies, where a program can read it without
parsing the message. The message is free.

An implementation MUST refuse:

1. `setext-heading`: a setext heading, at any depth (§4.1)
2. `indented-code`: an indented code block, at any depth, a marker line
   indented four or more columns included (§4.1, §7.1)
3. `link-reference-definition`: a link reference definition, at any depth
   (§4.1)
4. `raw-html`: an HTML block that is not a region marker, an HTML comment
   that does not match the marker line included (§4.1, §7.1)
5. `duplicate-name`: one name declared twice in one document (§7.4)
6. `conflict-marker`: a git conflict-marker line, anywhere in the file
   (§4.4)
7. `dangling-marker`: a marker that names no node: a one-line marker with no
   next sibling in its container or whose next sibling is a marker, or an
   empty region (§7.2, §7.3)
8. `unpaired-region`: a `:begin` and its `:end` that are not siblings in one
   container (§7.3)
9. `table-not-blank-above`: a table with a non-blank line directly above it
   in its container (§4.3)
10. `table-not-blank-below`: a table with a non-blank line directly below it
    in its container (§4.3)
11. `ambiguous-table`: a delimiter line and the paragraph line over it,
    judged without the line above, when either holds a form feed or a
    vertical tab, or when they are a table candidate with no unescaped pipe
    in one of the two lines (§4.3)

**Two orders between refusals are fixed** (0002, addendum on markers that
name nothing, and three defaults; addendum on ambiguous tables):

- when `duplicate-name` and `unpaired-region` both apply, the refusal is
  `duplicate-name`, and `dangling-marker` is reported after both: a document
  that also has a duplicate or unpaired name is refused for that;
- `ambiguous-table` is reported before `table-not-blank-above`.

**Any other order is unspecified.** A document to which two refusals apply
that neither order fixes, such as a setext heading and an indented code
block, may be refused with either. A conformance case asserts exactly one
identifier, so it is written so that only one refusal applies to it, or
combines only refusals whose order is fixed here.

## 10. Conformance

`conformance/cases/` holds the suite, as directories of exact bytes, one
`expect.json` each, under kindspec/kindkit's case-tree convention. It is
CC0, so it can be copied into an implementation in any language.
`conformance/cases/README.md` defines every field.

Every case has the one kind `parse`: the implementation reads `input.md` and
either refuses it, with one identifier from §9, or accepts it and reports:

- **frontmatter**: its line range, or none (§5);
- **blocks**: every block in order, with its type and its line range, which
  starts and ends on a non-blank line (§6.1). Line numbers count from 1 at
  the file's first line, frontmatter included;
- **leaves**: every leaf in document order, with its node path, type and
  content (§6.2, §6.3);
- **names**: every name a marker declares, and what it binds to (§7);
- **resolve**: for the names a case lists, what each resolves to (§8).

0002 §5 makes the tree pin the partition and the leaves, so each accepting
case lists every block, every leaf and every name, and a missing or extra
entry fails it.

`just conform` runs the tree against the reference reader,
`reference/blockspec/`. `just tree` checks the tree itself: that every case
can fail and every refusal has a control. `just mutants` reports mutants of
the reader that the tree does not kill.

## 11. Not decided

The adjudications leave these open. Where the suite pins one, it does so as
a **READING**, numbered as in `conformance/cases/README.md`, *Readings*.
Each is a question for a later decision, not an answer.

**Readings the suite pins:**

- **Reading 1.** Whether a region holds the other markers among its sibling
  nodes. The suite says it holds every sibling node between its markers,
  markers included.
- **Reading 2.** §4.3 states the table rule generally, as 0002's *Decision*
  does ("a blank line, or its container's edge, on both sides"). 0002 §6
  names its two refused shapes by a paragraph line above and a non-blank
  line below, and the suite reads the general rule, so a heading or a marker
  directly above a table is refused.
- **Reading 3.** Whether a `:begin` with no `:end` anywhere, or an `:end`
  with no `:begin`, is `unpaired-region`. The suite says it is.
- **Reading 6.** Whether `raw-html` reaches inline HTML. The suite reads it
  as block-level only, which follows from inline content being opaque
  (§4.2), but neither adjudication says so.
- **Reading 8.** What a leaf's content is, per type. The suite pins: a
  paragraph's raw content (CommonMark §4.8: each line's initial spaces or
  tabs removed, joined by `\n`, final spaces or tabs removed); a heading's
  raw content (CommonMark §4.2); a code block's lines between the fences,
  each ending in `\n`, with the fence's indentation removed and no info
  string; an HTML block's lines, each ending in `\n`; `""` for a thematic
  break; and for a table, its rows of cells, header first, each cell's text
  trimmed with `\|` read as `|`, a short row padded with `""` and cells past
  the header's width dropped.
- **Reading 9, in part.** That frontmatter ends at the **first** closing
  line, and that it may be empty (`---` on lines 1 and 2).
- **Reading 10.** That no blank line is needed after frontmatter.
- **Reading 11.** That an unclosed frontmatter block is not frontmatter, and
  its lines parse under the other rules.
- **Reading 12.** That frontmatter is opaque to the block rules but not to
  the conflict-marker scan. §4.4's "wherever it sits" follows from 0001's
  line scan before any block parsing; that the scan reaches inside
  frontmatter is the suite's reading.
- **Reading 13.** That frontmatter is not checked as YAML.
- **Reading 14.** The exact shape of a conflict-marker line: the suite reads
  a run of seven **or more** `<`, `>` or `|` followed by a space or the end
  of the line, or seven or more `=` alone on the line. D8 §7.2 says git emits
  runs of "7-or-more"; 0001 says seven.

**With no case:**

- **CRLF fixtures.** §3's `\n` rule is decided, but no fixture holds CRLF
  bytes yet (`conformance/cases/README.md`, *Not pinned yet*).
- **A byte-order mark, bytes that are not UTF-8, and U+0000.** No
  adjudication says whether each is refused, stripped or kept.
- **What a heading slug transcludes**: the heading, or its section (0002
  §4).
- **The anchor format**: how an anchor is stored and resolved, how it
  carries a disambiguator for a leaf already repeated when it is made, and
  how a range across leaves is written (0002 §2).
- **How this document ranks against the suite.** This document defers to
  the adjudications; whether, as in rowspec, the suite wins over this
  document where they disagree is not decided.
- **How refusal identifiers evolve**: whether a withdrawn identifier is
  retired and never reused, as rowspec's §9 says of its own.
- **The second opinion in CI** that 0001 proposes, an off-the-shelf
  CommonMark parser's block tree diffed against the reference's, is
  proposed, not adopted.
