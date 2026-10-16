<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# blockspec — specification, draft 0

Status: draft. This document writes up draft 0 as
`docs/adjudications/0001-syntax.md`, `0002-block.md` and
`0003-anchors.md` decide it, with their addenda. It answers nothing the
adjudications leave open; 0003 names the details §11 fixes beyond its
thirteen answers, and its addendum of 2026-10-16 decides the grammar and
the precision §11 states, the owner's decisions on the precision
included. Where an adjudication's wording had to be
scoped or read to give one answer, the text says so where it uses it,
marked **(read as)**. **Where this document and an adjudication disagree,
the adjudication wins
and this document is in error.** Where the adjudications are silent, this
document says so (§12) instead of choosing.

The conformance suite, `conformance/cases/`, was written from the same
adjudications before any implementation existed. Where they left a question
open, a case takes a reading and its `WHY.md` says **READING**. A reading is
not a decision, and §12 lists each one.

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
what each name binds to (§7), how a name resolves (§8), and how an anchor
or a transclusion resolves (§11). What a name names is also the unit a
transclusion takes: one node with its subtree, or the nodes of one region,
rendered as block content in the referrer (0002, *Decision*).

Not specified here: rendering, beyond what §11 says an anchor's status
shows; how a refusal is worded; editor behaviour; and anything about inline
content beyond keeping it as written and the one shape §4.2 names.

## 3. Encoding and lines

A document is UTF-8 text, one document per file, as `DESIGN-BRIEF.md` §1
decides. No refusal code exists yet for a file that is not UTF-8 (§12).

**U+0000 is replaced with U+FFFD**, as the pinned grammar requires
(CommonMark 0.31.2 §2.3, "Insecure characters").

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

**One exception**: a paragraph whose content is exactly one inline link
titled `transclude` is a transclusion (§11.9). 0003 Q5 amends 0001 to add
it. The paragraph is still a leaf, and its content is still its raw text.

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
(0002, *Decision*). That sentence decides the general rule: any non-blank
line directly above or below a table in its container, a heading or a
marker included, is refused, not only the two shapes 0002 §6 names. So:

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

A **lazy line** under a paragraph in a block quote or a list item, one
without that container's prefix, starts no table. If it starts another
block, that block begins: `- | -` starts a list item, as it does after any
paragraph line. Otherwise it is paragraph text, as CommonMark reads a lazy
continuation line, delimiter-shaped or not.

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
seven `|` for diff3's base marker (0001 §4). Whether the scan reaches a line
inside a fenced code block or inside frontmatter is not decided; the suite
reads that it does (§12, readings 4 and 12).

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
enclosing block (0002 §2). §11 gives the anchor format and its
resolution.

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

What that is per leaf type is the suite's reading (§12, reading 8).

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

**and is indented at most three spaces** (0001, addendum). Where the line
would start a block, four or more make it an indented code block, which §4.1
refuses. In paragraph context the same line is a paragraph continuation
line, so it is paragraph text, as CommonMark reads it. **(read as)**
0001's addendum says four or more make an indented code block; this document
reads that as applying where a block can start. The only spacing allowed is
spaces and tabs, inside and around the comment, so `<!--#intro-->` and
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

What a name resolves to is the node a marker binds (§7.2) or the nodes of a
region (§7.3). For a heading slug, whether it names the heading or its
section is not decided (0002 §4); the suite resolves a slug to the heading
node (§12).

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
available in either syntax (0001 §2). So a slug is not a transclusion target
(§11.9; 0003 §7).

## 9. Refusals — normative

A document is either accepted, with the structure §5–§8 describe, or refused.
**This list is complete**: every refusal draft 0 has is below, with the
identifier the conformance suite compares. An implementation reports the
identifier of the refusal it applies, where a program can read it without
parsing the message. The message is free.

An implementation MUST refuse:

1. `setext-heading`: a setext heading, at any depth (§4.1)
2. `indented-code`: an indented code block, at any depth, a marker line
   indented four or more columns where a block can start included (§4.1,
   §7.1)
3. `link-reference-definition`: a link reference definition, at any depth
   (§4.1)
4. `raw-html`: an HTML block that is not a region marker, an HTML comment
   that does not match the marker line included (§4.1, §7.1)
5. `duplicate-name`: one name declared twice in one document (§7.4)
6. `conflict-marker`: a git conflict-marker line (§4.4)
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
- `ambiguous-table` is reported before `table-not-blank-above` when both
  apply to the same table's lines. **(read as)** The addendum on markers that
  name nothing states this order in general terms; the addendum on
  ambiguous tables states it for one pair of lines ("If the two lines alone
  are `ambiguous-table`, so is the document, which takes precedence over
  `table-not-blank-above`"), and this document reads the general sentence
  that way. When the two refusals arise from different tables, their order
  is unspecified, like any other.

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

## 11. Anchors and transclusion

Decided by `docs/adjudications/0003-anchors.md`, which gives the reason for
each rule below and the edit shape it exists for. **An anchor resolves only
where every witness it has agrees. Any disagreement, any tie and any missing
witness is loud** (0003 §1). Nothing here writes into the document an
anchor or a transclusion points at.

This section specifies what the format guarantees from two snapshots of a
document: `base`, the blob an anchor was made against, and the current
text. §11.11 says what a tool MAY add on top, and §11.12 what no tool
reading only those snapshots can prevent.

### 11.1 Records

**A comment or a suggestion is a record: one file per record, in
`<doc>.notes/` beside its document** (0003 Q1). For `policy.md` that is
`policy.md.notes/`. The directory is authoritative for which document a
record belongs to, and a record holds no path (0003 Q9).

- **A record's file name is `<id>.md`**, where `<id>` is a ULID (D8 §7.4):
  26 characters of Crockford's base 32 in upper case, `[0-9A-HJKMNP-TV-Z]`,
  the first of them `0` to `7`. Ids are unique within a notes directory. An
  id is never written into the document.
- **Everything in a notes directory is a record.** A file whose name is not
  `<id>.md` in that form, and a subfolder, are each
  `REFUSED(record-inconsistent)` (0003, second addendum of 2026-10-16,
  item 5).
- **A record is a blockspec document.** Its frontmatter holds the anchor and
  the metadata. Its body is the comment.
- **The anchor is one line**, `anchor:` followed by a JSON object, and **at
  least one line that is not edited freely separates it from any line that
  is**, such as `kind:` before `status:`.
- **A reply is its own record**, with a `reply-to` line naming a record in
  the same directory, and no anchor.

The anchor's fields:

| field | value |
| --- | --- |
| `base` | the full object id of the document's blob that the anchor was made against |
| `leaf.type` | `p`, `h1` to `h6`, `code` or `table`: a paragraph, a heading with its level, a code block or a table |
| `leaf.text` | the leaf's content (§6.3), normalised to Unicode NFC, with `\n` line endings; for a table, the string §11.2 defines |
| `leaf.nth` | the 0-based ordinal of the leaf among the leaves of `base` with the same type and text |
| `span`, `prefix`, `suffix` | a W3C TextQuoteSelector inside `leaf.text`. `prefix` is the 32 code points before `span`, and `suffix` the 32 after it, or fewer where the leaf's edge is nearer. Neither crosses the leaf's edge |
| `replace` | a suggestion's replacement text; absent on a comment |

The other fields: `kind` is `comment` or `suggestion`, and `status` is
`open`, `accepted`, `rejected` or `resolved`.

**The frontmatter's grammar** (0003, addendum of 2026-10-16, detail 1). The
lines between the record's opening and closing `---` (§5) are exactly these,
in this order, each with nothing before or after it:

- a comment or a suggestion: `anchor: ` followed by the anchor, then
  `kind: comment` or `kind: suggestion`, then `status: ` followed by one of
  the four statuses;
- a reply: `reply-to: ` followed by the parent's id as a JSON string, then
  `kind: comment`.

The anchor is a JSON object (RFC 8259), which is also a YAML 1.2 flow
mapping, written in one canonical form:

    {"base": B, "leaf": {"type": T, "nth": N, "text": S}, "span": S, "prefix": S, "suffix": S}

with `, "replace": S` before the final `}` for a suggestion, and never for a
comment. The keys are in the order shown.

- `B` is a string holding `base` in lower-case hex: 40 digits in a SHA-1
  repository, 64 in a SHA-256 one.
- `T` is a string, one of `p`, `h1` to `h6`, `code` and `table`.
- `N` is decimal digits, `0` or with no leading zero, and no sign, fraction
  or exponent.
- **Strings.** Each `S`, and the `reply-to` id, is `"`, its code points, then
  `"`. `"` is written `\"`, `\` is written `\\`, and a line feed is written
  `\n`. Every other code point in U+0000 to U+001F, in U+007F to U+009F, and
  U+2028, U+2029, U+FEFF, U+FFFE and U+FFFF is written `\u` followed by four
  lower-case hex digits. Every other code point is written as itself, in
  UTF-8. No other escape is used.
- **Spacing.** One space after each `:` and after each `,` between members,
  and none anywhere else.

For example, with an illustrative `base`:

    ---
    anchor: {"base": "9b1c4e0d2f7a6385c1e0b4d9a8f7263514c0e9ab", "leaf": {"type": "p", "nth": 0, "text": "The reactor scram threshold is 4.2 sigma above baseline, measured over a rolling 30-second window."}, "span": "4.2 sigma", "prefix": "The reactor scram threshold is ", "suffix": " above baseline, measured over a"}
    kind: comment
    status: open
    ---

A reader that parses the value as JSON and writes it back in this form can
compare the bytes.

**Offsets are code points of `leaf.text`**, the NFC-normalised parsed
content, never offsets into the file.

**Creation.** In the commit that adds a record, `base` is the document's
blob in that commit, `leaf` at `nth` exists in `base`, and
`prefix + span + suffix` occurs exactly once in `leaf.text`. Where it does
not occur exactly once, the anchor is not created.

**Occurrences are counted by start position** (0003, third addendum of
2026-10-16, item 1), here, in the consistency check below and in §11.5's
hits alike: two occurrences that overlap are two. (Applying it to §11.5 is
that addendum's precision, not the owner's ruling.)

**Consistency.** A record is `REFUSED(record-inconsistent)` when `leaf` at
`nth` is not in `base`; when `prefix + span + suffix` does not occur exactly
once in `leaf.text`; when `prefix` or `suffix` is shorter than 32 code
points while the leaf's edge is further away; or when `span` is empty (0003,
the details it fixes). It is also `REFUSED(record-inconsistent)` (0003,
addendum, detail 1) when it has no frontmatter; when the frontmatter's lines
are not exactly those above, in that order, with nothing added; when the
anchor or the `reply-to` id is not in the canonical form, including a value
that is valid JSON or YAML and reads to the same values written another way
(other spacing, key order or escapes, a duplicate key, an unquoted key);
when `B` or `T` is not a value the list above allows; or when `replace` is
present on a comment or missing on a suggestion. And it is
`REFUSED(record-inconsistent)` (0003, second addendum of 2026-10-16) when
`prefix` or `suffix` is longer than 32 code points (item 1); when its
`reply-to` string is not a ULID in the form above (item 5); or when the
profile refuses its body (item 8), since a record is a blockspec document.

**Re-anchoring** replaces the whole anchor line with one made against a
newer blob of the document, at the position the current resolution gives. It
is done only while the anchor resolves `RESOLVED` or `EDITED` (§11.6).

### 11.2 Leaves, keys and similarity

The resolver works on each snapshot's **text-bearing leaves**, in document
order: paragraphs, headings, code blocks and tables. HTML blocks (markers)
and thematic breaks take no part.

A leaf's **key** is its `leaf.type` and its `leaf.text`. Two leaves are
**copies** when their keys are equal. A heading that changes level changes
its key.

**A table's text** is one string (0003, addendum, detail 3). Its cells, as
the suite's reading 8 normalises them (header row first, each cell trimmed
of spaces and tabs, `\|` read as `|`, a short row padded with `""`, cells past
the header's width dropped), each have every `|` written as `\|`; they are
joined by ` | ` within a row and the rows by `\n`; and the result is
normalised to NFC. The escape keeps the string unambiguous: a `|` from a
cell follows a `\`, and a separator's follows a space, which a trimmed cell
never ends in. Without it, a one-cell row `a | b` and a two-cell row `a`,
`b` would be copies.

The **similarity** of two leaves is `2·L/(m+n)`, where `m` and `n` are the
lengths in code points of their keys, each written as the type, U+001F and
the text, and `L` is the length of a longest common subsequence of the two.

A **longest common subsequence alignment** of two sequences pairs elements
from the start: when the two elements under consideration are equal they
are paired;
otherwise the element of the first sequence is skipped if that does not
shorten the longest common subsequence of what remains, and the element of
the second is skipped if it does.

### 11.3 Correspondence

Correspondence pairs base leaves with current leaves (0003 §4):

1. **The chain.** Take each key that occurs exactly once in `base` and
   exactly once in the current text, as a pair of positions. The longest
   subsequence of those pairs, in base order, whose current positions
   increase is the **chain**. Its pairs are `EXACT`. Every other such pair
   is `MOVED`. **When several subsequences are longest, the chain is the
   leftmost** (0003, addendum, detail 4): number the current text-bearing
   leaves from 0 in document order; the chain is the one whose sequence of
   current indices, in base order, is lexicographically smallest, so at the
   first position where two differ, the smaller index wins. The sequence
   identifies the chain, since its keys are unique in the current text.
2. **Gaps.** The chain cuts each snapshot into gaps: the leaves between two
   consecutive chain pairs, before the first, or after the last, leaving out
   leaves paired as `MOVED`. Inside each gap, the longest common subsequence
   alignment (§11.2) of the base leaves' keys onto the current leaves' keys
   gives further `EXACT` pairs.
3. **Edits.** A base leaf `i` and a current leaf `j` left over in the same
   gap pair as `EDITED` when all of these hold: their similarity is at least
   0.5; it exceeds the similarity of `i` to every other leftover current
   leaf in the gap by at least 0.15; and it exceeds the similarity of `j` to
   every other leftover base leaf in the gap by at least 0.15.

A current leaf that is no base leaf's pair is **unmatched**.

**Thresholds compare exactly, in integer arithmetic** (0003, addendum,
detail 5). With a similarity written `2·L/T`, where `T = m+n` is at least 2:

| §11 states | compare |
| --- | --- |
| similarity at least 0.5 | `4·L ≥ T` |
| similarity below 1 | `2·L < T` |
| `2·L₁/T₁` exceeds `2·L₂/T₂` by at least 0.15 | `40·L₁·T₂ − 40·L₂·T₁ ≥ 3·T₁·T₂` |

These apply wherever §11.3 and §11.4 compare a similarity with 0.5, 1 or a
margin of 0.15. A floating-point comparison is not conforming:
`22/30 − 42/72` is exactly 0.15, and IEEE 754 doubles compute it as just
below.

### 11.4 The anchored leaf

The anchored leaf `k` is the leaf of `base` with key `leaf.type` and
`leaf.text`, at ordinal `nth`. Its **gap** is bounded by the nearest chain
pair before `k` and the nearest after it, in base order, or by a snapshot's
edge where there is none. On the base side the gap is the leaves strictly
between those two pairs' base positions, and on the current side the leaves
strictly between their current positions.

`k`'s pair, if it has one, is then checked, and the first rule that applies
decides (0003 §4):

- **No pair**: `REFUSED(unaccounted-copy)` if any current leaf is a copy of
  `k`, and `ORPHANED` otherwise.
- **`EXACT`**:
  - if `base` or the current text holds more than one copy of `k`, the
    number of copies in `k`'s gap must be equal on both sides, or
    `REFUSED(repeat)`. The pair always lies in the gap: a repeated key is
    never on the chain, so `k`'s `EXACT` pair comes from §11.3 step 2's
    alignment inside `k`'s own gap (0003, second addendum of 2026-10-16,
    item 9);
  - an unmatched leaf with similarity to `k` of at least 0.5 and below 1:
    `REFUSED(near-copy)`.
- **`MOVED`**:
  - an unmatched leaf with similarity to `k` of at least 0.5:
    `REFUSED(near-copy)`;
  - an unmatched leaf in `k`'s gap on the current side:
    `REFUSED(refilled-gap)`.
- **`EDITED`**:
  - an unmatched copy of `k`: `REFUSED(exact-copy)`. A copy that is some
    base leaf's pair does not count (0003 Q12);
  - another unmatched leaf in `k`'s gap on the current side:
    `REFUSED(crowded-gap)`;
  - an unmatched leaf with similarity to `k` of at least 0.5:
    `REFUSED(near-copy)`.

### 11.5 The span

For `EXACT` and `MOVED`, the span keeps its offset in the paired leaf, whose
text is unchanged.

For `EDITED`, the span is searched **inside the paired leaf only**. A hit is
an occurrence of `span` with `prefix` ending where it starts and `suffix`
starting where it ends. **A short context must sit at the leaf's edge**
(0003, addendum, detail 6): when `prefix` is shorter than 32 code points,
the hit's `prefix` starts at the start of the paired leaf's text, and when
`suffix` is shorter than 32, the hit's `suffix` ends at its end. An
occurrence that does not is not a hit. Hits are counted by start position,
overlapping ones included (§11.1). With no hit the anchor is
`DETACHED`; with more than one, `REFUSED(span-ambiguous)`. With one hit, the
longest common subsequence alignment (§11.2) of the base leaf's text onto
the paired leaf's text must pair every code point of the span with the code
point at the same position in the hit, or the anchor is `DETACHED` (0003
§5).

There is no fallback that places a comment without its context (0003 Q13).

### 11.6 Statuses

| status | meaning | renders as |
| --- | --- | --- |
| `RESOLVED` | `EXACT`, and the span found | the anchor |
| `MOVED` | `MOVED`, and the span found | the anchor, marked moved |
| `EDITED` | `EDITED`, and the span found | the anchor, marked changed |
| `DETACHED` | the leaf has a pair, and the span does not survive in it | on the paired leaf, flagged, with the text as it stood at `base` |
| `ORPHANED` | the leaf has no pair | `#REF!`, with the text as it stood at `base` |
| `REFUSED(reason)` | a rule of §11.4 or §11.5 applies, or an input is unusable (§11.10) | `#REF!(reason)`, with the text as it stood at `base` where it is available |

`DETACHED`, `ORPHANED` and `REFUSED` are loud: they render in place, with
their reason (D8 §10).

### 11.7 Suggestions

**A suggestion applies only when its record's `status` is `open` and its
anchor is `RESOLVED` or `EDITED`** (0003 Q2, Q10). Otherwise it is stale. A
suggestion is never applied on `MOVED`. An accepted or rejected suggestion
renders as history, never as an edit that can be applied.

**Accepting** a suggestion changes the document and sets `status: accepted`
in one commit.

**Write-back** (0003 Q11). Through the parse, each code point of the leaf's
content comes from one raw character of its lines. Container prefixes (`>`
markers and list-item indentation), the indentation a paragraph line loses,
and line endings, carriage returns included, are raw characters no content
code point comes from; a `\n` in the content stands for the line ending,
whichever it is. In a file whose lines end in a bare CR, that `\n` comes
from the CR.

1. Let `a` and `b` be the positions in the leaf's content, before NFC, such
   that the NFC form of the content before `a` is `leaf.text` before the
   span, and the NFC form of the content from `a` to `b` is `span`. If there
   are no such positions, the span does not map.
2. Map `a` and `b` through the parse to raw positions, skipping the
   characters above. The raw text between them is the span's raw range.
3. Replace the range with `replace`, written exactly as stored and never
   normalised, except at its line breaks. Each `\n` in `replace` is written
   as the line ending of the line it breaks (CRLF in a CRLF file, CR in a
   bare-CR file), and each new line is preceded by the container prefixes
   the parse gives the line it continues. Nothing outside the range
   changes.

Only the span's own text must match after NFC; the rest of the leaf may be
in any normalisation form and may span several prefixed or CRLF lines.
Where the span does not map, the suggestion is stale, with the reason
`unmappable-offset`.

**A line break that cannot be written back** (0003, second addendum of
2026-10-16, item 4). A `\n` in `replace` makes the suggestion stale, as
`unmappable-offset`, when the line it breaks is a list item's first line,
whose container prefix is the list marker; a lazy line, which has no
container prefix; a line whose container prefix holds a tab; or the file's
last line, when the file has no final line ending.

**Two spans that cannot be written back** (0003, third addendum of
2026-10-16, items 3 and 4). The suggestion is stale, as `unmappable-offset`,
when:

- a code point of the span comes from no single raw character: the rest of
  a tab only partly consumed by container indentation, which CommonMark
  keeps as spaces in the content. A span that only begins or ends next to
  such a character maps (that reading of "crosses" is the addendum's
  precision);
- the span ends at a code block's final line ending, the `\n` that ends its
  last content line, since writing it back would join the closing fence to
  the line before it. That holds whatever `replace` ends with (the
  addendum's precision).

### 11.8 Replies, deletion and document identity

- **Records are not deleted in normal use** (0003 Q8). A suggestion is
  accepted or rejected by its `status`. A purge removes a whole thread, the
  record and every reply to it, in one commit.
- **A reply whose `reply-to` names no record in its directory** renders as
  `#REF!(reply-to)`, once its document checks pass (§11.10).
- **A commit that renames a document moves its notes directory in the same
  commit** (0003 Q9).
- **A record id found in more than one notes directory is warned on** (0003
  Q9). It is a warning, not a refusal.

### 11.9 Transclusion

**A transclusion is a paragraph whose content is exactly one inline link
with the title `transclude`** (0003 Q5):

    [Scram threshold](policy.md#scram-threshold "transclude")

This is the one inline shape the profile gives meaning to (§4.2). The link's
destination is `path#name`, where `path` is the target document and `name`
is a region marker's name in it (§7). A heading slug is not a target. The
link renders as a link in any markdown tool.

**The path** (0003, addendum, detail 7) is the destination's part before the
`#` (CommonMark 0.31.2, *Links*), **as raw text**: character for character
as the file writes it, with no backslash escape, entity reference or
percent-encoding decoded. That is also the text a pin's `path` holds, and
this definition governs both. So `my%20doc.md` names a file called
`my%20doc.md`. It resolves relative to the directory that
holds the referrer, as a renderer resolves a relative link, in the tree of
the snapshot being resolved: it is split at `/`, a `.` segment is dropped,
and a `..` segment removes the segment before it.

- A path that begins with `/`, or whose first segment holds a `:`, is
  absolute, and is `REFUSED(unresolvable-path)`.
- A `..` that would go above the repository's root is
  `REFUSED(unresolvable-path)`.
- A path that names no file in that tree is `REFUSED(document-missing)`.
  Names compare exactly, case included.

**The unit transcluded is what the name binds** (0002 §4): one node with its
subtree, or the nodes of one region. It renders as block content in the
referrer, and it is never copied into the referrer's file (D8 §8.1, D8's
R3).

**The referrer pins each target**: its frontmatter records, for each target
it transcludes, the target document's blob at the time it was pinned (0003
§7; D8 §7.3).

**How pins are written** (0003, addendum, detail 2): a line of the
referrer's frontmatter that is exactly `pins:`, directly followed by one
line per pin, each `  - ` (two spaces, a hyphen and a space) followed by an
object in §11.1's canonical form and string escaping:

    pins:
      - {"path": "policy.md", "blob": "9b1c4e0d2f7a6385c1e0b4d9a8f7263514c0e9ab"}

- `path` is the path part of a transclusion's destination, as raw text
  (above). A transclusion uses the pin whose `path`
  is equal to its own.
- `blob` is the target document's blob when it was pinned, in lower-case hex
  as §11.1's `B`.
- The pins end at the first frontmatter line that does not begin with
  `  - `. They are sorted by `path`, ascending, code point by code point, and
  no `path` appears twice.
- A line that begins with `  - ` after the pins have ended is refused when
  every line between them is blank or begins with a space or `#`: a YAML
  reader would read it as one more pin, across a blank or comment line.

The rest of the frontmatter stays opaque (§5): the resolver reads the pin
lines as text, not through a YAML reader. **Every transclusion in the
referrer is `REFUSED(record-inconsistent)`** when the frontmatter has more
than one line that begins with `pins:`, a line that begins with `pins:` and
is not exactly `pins:`, a pin line not in the canonical form, pins out of
order, one `path` twice, or such a `  - ` line after the pins have
ended.

Two branches that add or re-pin different targets merge cleanly when an
unchanged line lies between their changes, and conflict when the changes
touch (0003, addendum, detail 2).

**Resolution**, against the target's current text. A name **binds** only
through a region marker (§7.2, §7.3); a heading slug never binds (0003,
second addendum of 2026-10-16, item 6).

0. **The referrer.** A referrer the profile refuses is refused as a whole,
   `REFUSED(not-in-profile)`, and its transclusions are not enumerated: a
   refused file has no tree to find them in. A conflict-marker line
   anywhere in it counts, in its frontmatter and in a fenced code block
   alike, whatever readings 4 and 12 say (same addendum, item 7).
1. **The inputs**, checked in this order; the first that fails decides
   (same addendum, items 2 and 3, with its precision):
   1. the path must resolve, or `REFUSED(unresolvable-path)`;
   2. the referrer's pins must follow the grammar above, or
      `REFUSED(record-inconsistent)`;
   3. the target document must exist, or `REFUSED(document-missing)`;
   4. the current target must pass the profile, or
      `REFUSED(not-in-profile)`;
   5. a name that only a heading slug matches in the current target is
      `#REF!(name)` (item 6). A marker name that is also some heading's
      slug resolves to the marker (§8.1);
   6. the pinned blob must be readable, or `REFUSED(base-unavailable)`;
   7. the pinned blob must pass the profile, or `REFUSED(not-in-profile)`;
   8. a marker must bind the name in the pinned blob, or
      `REFUSED(record-inconsistent)`.
2. **The name** resolves as §8.1 says, against markers only. No match is
   `#REF!(name)`. There is never more than one: step 1 requires the current
   target to pass the profile, which refuses a name declared twice (§7.4;
   same addendum, item 9).
3. For each text-bearing leaf the name binds in the pinned blob, §11.3 and
   §11.4 run with that blob as `base`. A refusal, or no pair, refuses the
   transclusion, as `REFUSED(pinned-<reason>)`, where `<reason>` is §11.4's
   reason or `orphaned`. Where several leaves refuse, the first in the
   pinned blob's document order is reported.
4. Each pair must lie inside what the name binds now. Otherwise the
   transclusion is `REFUSED(name-rebound)`.

A refused transclusion stays refused until the referrer re-pins, recording
the target's current blob (0003 Q4).

### 11.10 Resolution reasons

A refused anchor or transclusion renders `#REF!(reason)` with one of these
reasons. They are resolution outcomes, not refusals of a document, so they
are not in §9's list.

| reason | applies when |
| --- | --- |
| `unresolvable-path` | a transclusion's path is absolute, or a `..` in it goes above the repository's root (§11.9) |
| `document-missing` | the notes directory's document, or a transclusion's target, does not exist |
| `base-unavailable` | the `base` blob, or a pin's blob, cannot be read |
| `not-in-profile` | `base`, the current text, a pinned blob or a transclusion's current target is refused under §9, a file committed with conflict markers included; or the referrer is, which refuses it as a whole (§11.9, step 0) |
| `record-inconsistent` | §11.1's consistency rules fail, an entry of a notes directory is not a record, the referrer's pins break §11.9's grammar, or a pinned name binds nothing in its pinned blob |
| `unaccounted-copy` | §11.4, no pair |
| `repeat` | §11.4, `EXACT` |
| `near-copy` | §11.4, `EXACT`, `MOVED` or `EDITED` |
| `refilled-gap` | §11.4, `MOVED` |
| `exact-copy` | §11.4, `EDITED` |
| `crowded-gap` | §11.4, `EDITED` |
| `span-ambiguous` | §11.5 |
| `name-rebound` | §11.9, step 4 |
| `pinned-<reason>` | §11.9, step 3 |

A transclusion whose name no marker binds in the current target renders
`#REF!(name)` (§11.9, steps 1 and 2).

**Which reason is reported** (0003, second addendum of 2026-10-16, item 2).
When a record has several input problems, the first in data-dependency order
is reported:

1. the record's grammar (`record-inconsistent`);
2. `document-missing`;
3. the current document refused under the profile (`not-in-profile`);
4. `base-unavailable`;
5. `base` refused under the profile (`not-in-profile`);
6. the leaf at `nth` inconsistent with `base` (`record-inconsistent`).

**A reply is a record** (0003, third addendum of 2026-10-16, item 2): a
reply whose document is missing, or refused by the profile, is
`REFUSED(document-missing)` or `REFUSED(not-in-profile)`. It goes through
steps 1 to 3; steps 4 to 6 read an anchor, which a reply does not have. Only
a reply that passes steps 1 to 3 is looked up by its `reply-to`, and renders
`#REF!(reply-to)` when that names no record. (Where the reply sits in the
order is the addendum's precision.)

Step 1 holds every check that reads only the record, `leaf.text` included:
its file name and directory entry, its frontmatter, its body, an empty
`span`, a context longer than 32 code points, `prefix + span + suffix` not
occurring exactly once in `leaf.text`, and a short context whose edge in
`leaf.text` is further away. Step 6 holds the one check that needs `base`'s
leaves: no leaf of `base` with `leaf`'s type and text at ordinal `nth`. So
a record whose triple occurs twice in its `leaf.text`, and whose `base`
cannot be read, is `record-inconsistent`. (That split is the addendum's
precision, not the owner's ruling.)

A transclusion's order is §11.9's steps 0 to 4, read in order: the referrer
first, then the inputs in step 1's order, with the pin in the place of
`base`. Several `pinned-<reason>`s are ordered by their leaves in the
pinned blob's document order, and the first is reported. (The transclusion
order beyond items 2, 3, 6 and 7, and the leaves' order, are the
addendum's precision.)

A stale suggestion carries `unmappable-offset` when §11.7's mapping fails.
A reply with no parent renders `#REF!(reply-to)`.

### 11.11 What a tool MAY add

None of these is part of the format, and correctness does not depend on any
of them (0003 §1).

- **Re-base before landing** (0003 Q3). A squash-merge or a rebase can
  leave a record's `base` in no commit that a fresh clone has. Before the
  branch lands, while `base` is still reachable, a tool MAY re-anchor
  (§11.1) each record that resolves `RESOLVED` or `EDITED` onto the
  document's blob at the branch head. It MAY check in CI that every record
  that resolves has been re-based; a record that does not resolve keeps its
  `base` and is reported, and does not fail the landing. Once its `base` is
  gone, such a record is `REFUSED(base-unavailable)`. This turns a future
  `base-unavailable` into a resolution, so it is not a refusal rule.

The other two MAY only refuse more, never turn a refusal into a resolution:

- **Resolve through merge parents** (0003 Q7), refusing when the parents
  disagree.
- **Track document identity** (0003 Q9) across renames and copies, and
  refuse a record it can tell belongs to another document.

### 11.12 What this does not prevent

Four mechanisms leave current bytes identical to those a legitimate edit
produces, so they resolve, silently, to the wrong text (0003 §9):

| | mechanism | indistinguishable from | suggestions |
| --- | --- | --- | --- |
| R1 | a leaf deleted, and a verbatim copy of it elsewhere | a move | not affected: stale on `MOVED` |
| R2 | a leaf rewritten to similarity below 0.5, with a verbatim copy of its old text left in its place in order | a new leaf inserted beside an unchanged one | affected |
| R3 | inside one leaf, the span's sentence rewritten and the old sentence re-added with the same context | a sentence moved within its leaf | affected |
| R4 | a different document at the same path, by archive-and-replace or copy-and-rewrite | an edit of the document | affected |

## 12. Not decided

The adjudications leave these open. Where the suite pins one, it does so as
a **READING**, numbered as in `conformance/cases/README.md`, *Readings*.
Each is a question for a later decision, not an answer.

**Readings the suite pins:**

The suite's reading 2, a non-paragraph line directly above a table, is not
listed: 0002's *Decision* text decides it (§4.3).

- **Reading 1.** Whether a region holds the other markers among its sibling
  nodes. The suite says it holds every sibling node between its markers,
  markers included.
- **Reading 3.** Whether a `:begin` with no `:end` anywhere, or an `:end`
  with no `:begin`, is `unpaired-region`. The suite says it is.
- **Reading 4.** Whether a conflict-marker line inside a fenced code block
  is refused. 0001 §4 describes the refusal as a line scan before any block
  parsing; the suite reads that the scan reaches inside a fence.
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
  the header's width dropped. 0003's addendum builds a table's text for §11
  from those cells (§11.2), so changing this reading changes every table's
  key.
- **Reading 9, in part.** That frontmatter ends at the **first** closing
  line, and that it may be empty (`---` on lines 1 and 2).
- **Reading 10.** That no blank line is needed after frontmatter.
- **Reading 11.** That an unclosed frontmatter block is not frontmatter, and
  its lines parse under the other rules.
- **Reading 12.** That frontmatter is opaque to the block rules but not to
  the conflict-marker scan, read, as reading 4 is, from 0001 §4's line scan
  before any block parsing.
- **Reading 13.** That frontmatter is not checked as YAML.
- **Reading 14.** The exact shape of a conflict-marker line: the suite reads
  a run of seven **or more** `<`, `>` or `|` followed by a space or the end
  of the line, or seven or more `=` alone on the line. D8 §7.2 says git emits
  runs of "7-or-more"; 0001 says seven.

**With no case:**

- **CRLF fixtures.** §3's `\n` rule is decided, but no fixture holds CRLF
  bytes yet (`conformance/cases/README.md`, *Not pinned yet*).
- **A byte-order mark, and bytes that are not UTF-8.** No adjudication
  says whether each is refused, stripped or kept, and neither has a refusal
  code.
- **What a heading slug names** for resolution: the heading, or its section
  (0002 §4). The suite resolves it to the heading. A slug is not a
  transclusion target either way (§11.9).
- **A range anchor**, a selection across leaves (0002 §2; 0003, *Effect on
  0001, 0002 and draft 0's documents*).
- **How this document ranks against the suite.** This document defers to
  the adjudications; whether, as in rowspec, the suite wins over this
  document where they disagree is not decided.
- **How refusal identifiers evolve**: whether a withdrawn identifier is
  retired and never reused, as rowspec's §9 says of its own.
- **The second opinion in CI** that 0001 proposes, an off-the-shelf
  CommonMark parser's block tree diffed against the reference's, is
  proposed, not adopted.

**Left open by 0003:**

- **Transclusion details**: a destination with no path, a destination in
  angle brackets, the title's other quoting forms (`'transclude'`,
  `(transclude)`), a title written with backslash escapes or entity
  references, a `transclude` link in a paragraph
  that holds other text, a transclusion paragraph inside a list item or a
  block quote, a transclusion with no pin, and a document that transcludes
  itself, directly or through another.
- **What a validator reports** for a rename that leaves its notes directory
  behind, and for a record id in two notes directories, and whether either
  has an identifier.
- **Thresholds.** 0.5 and 0.15 are borrowed from D8's `difflib` ratios and
  applied here to `2·L/(m+n)`, a different measure. They are untested for
  this resolver (0003 §4).

**Raised by 0003's addendum of 2026-10-16:**

- **Whether creation and the consistency check count under the edge rule.**
  §11.1 requires `prefix + span + suffix` to occur exactly once in
  `leaf.text`, counting every occurrence; §11.5 counts a hit only at the
  edge when a context is short. A triple that occurs once at the edge and
  again elsewhere is not created, and a record holding it is
  `record-inconsistent`, though under the edge rule it is unambiguous.
- **Whether a later version admits further keys in a record's
  frontmatter**, such as an author or a time. Draft 0 refuses them
  (§11.1).
- **A pin that no transclusion uses.** §11.9 says which pin a transclusion
  uses, and nothing about a pin left over.
- **Frontmatter that hides the pins line.** The resolver reads the pin lines
  as text. Other frontmatter content, such as a multi-line scalar, could make
  a YAML reader read a `pins:` line differently.
- **Writing a suggestion back into a table.** A table's text holds
  separators, escapes and padding that no single raw character gives, so
  §11.7's mapping does not say how a span in a table, or one that crosses a
  cell, maps to the file.
- **Whether a renderer-style decoding of a path is wanted later.** §11.9
  reads a path as raw text, so a percent-encoded, backslash-escaped or
  entity-encoded path names the file spelled that way, or is
  `document-missing`. How an empty segment (`a//b.md`) is read is not
  decided.
- **A path that names a symbolic link, a submodule, or a file that is not
  markdown.**
