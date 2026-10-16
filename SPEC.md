<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# blockspec — specification, draft 0

Status: draft. This document writes up draft 0 as
`docs/adjudications/0001-syntax.md`, `0002-block.md` and
`0003-anchors.md` decide it, with their addenda. It answers nothing the
adjudications leave open; 0003 names the details §11 fixes beyond its
thirteen answers. Where an adjudication's wording had to be scoped or read
to give one answer, the text says so where it uses it, marked **(read as)**.
**Where this document and an adjudication disagree, the adjudication wins
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

- **A record's file name is `<id>.md`**, where `<id>` is a ULID (D8 §7.4).
  Ids are unique within a notes directory. An id is never written into the
  document.
- **A record is a blockspec document.** Its frontmatter holds the anchor and
  the metadata. Its body is the comment.
- **The anchor is one line**, `anchor:` followed by a YAML flow mapping, and
  **at least one line that is not edited freely separates it from any line
  that is**, such as `kind:` before `status:`.
- **A reply is its own record**, with `reply-to: <id>` naming a record in the
  same directory, and no anchor.

The anchor's fields:

| field | value |
| --- | --- |
| `base` | the full object id of the document's blob that the anchor was made against |
| `leaf.type` | `p`, `h1` to `h6`, `code` or `table`: a paragraph, a heading with its level, a code block or a table |
| `leaf.text` | the leaf's content (§6.3), normalised to Unicode NFC, with `\n` line endings |
| `leaf.nth` | the 0-based ordinal of the leaf among the leaves of `base` with the same type and text |
| `span`, `prefix`, `suffix` | a W3C TextQuoteSelector inside `leaf.text`. `prefix` is the 32 code points before `span`, and `suffix` the 32 after it, or fewer where the leaf's edge is nearer. Neither crosses the leaf's edge |
| `replace` | a suggestion's replacement text; absent on a comment |

The other fields: `kind` is `comment` or `suggestion`, and `status` is
`open`, `accepted`, `rejected` or `resolved`.

**Offsets are code points of `leaf.text`**, the NFC-normalised parsed
content, never offsets into the file.

**Creation.** In the commit that adds a record, `base` is the document's
blob in that commit, `leaf` at `nth` exists in `base`, and
`prefix + span + suffix` occurs exactly once in `leaf.text`. Where it does
not occur exactly once, the anchor is not created.

**Consistency.** A record is `REFUSED(record-inconsistent)` when `leaf` at
`nth` is not in `base`; when `prefix + span + suffix` does not occur exactly
once in `leaf.text`; when `prefix` or `suffix` is shorter than 32 code points
while the leaf's edge is further away; or when `span` is empty (0003, the
details it fixes).

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
   is `MOVED`.
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
    number of copies in `k`'s gap must be equal on both sides, and the pair
    must lie in the gap, or `REFUSED(repeat)`;
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
starting where it ends. With no hit the anchor is `DETACHED`; with more than
one, `REFUSED(span-ambiguous)`. With one hit, the longest common subsequence
alignment (§11.2) of the base leaf's text onto the paired leaf's text must
pair every code point of the span with the code point at the same position in
the hit, or the anchor is `DETACHED` (0003 §5).

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

### 11.8 Replies, deletion and document identity

- **Records are not deleted in normal use** (0003 Q8). A suggestion is
  accepted or rejected by its `status`. A purge removes a whole thread, the
  record and every reply to it, in one commit.
- **A reply whose `reply-to` names no record in its directory** renders as
  `#REF!(reply-to)`.
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

**The unit transcluded is what the name binds** (0002 §4): one node with its
subtree, or the nodes of one region. It renders as block content in the
referrer, and it is never copied into the referrer's file (D8 §8.1, D8's
R3).

**The referrer pins each target**: its frontmatter records, for each target
it transcludes, the target document's blob at the time it was pinned (0003
§7; D8 §7.3).

**Resolution**, against the target's current text:

0. The target document must exist, or `REFUSED(document-missing)`, and the
   pinned blob must be readable, or `REFUSED(base-unavailable)`. Both the
   pinned blob and the current target must pass the profile, or
   `REFUSED(not-in-profile)`. The name must bind in the pinned blob, or
   `REFUSED(record-inconsistent)`.
1. The name resolves as §8.1 says, against markers only. Zero matches, or
   more than one, is `#REF!(name)`.
2. For each text-bearing leaf the name bound in the pinned blob, §11.3 and
   §11.4 run with that blob as `base`. A refusal, or no pair, refuses the
   transclusion, as `REFUSED(pinned-<reason>)`, where `<reason>` is §11.4's
   reason or `orphaned`.
3. Each pair must lie inside what the name binds now. Otherwise the
   transclusion is `REFUSED(name-rebound)`.

A refused transclusion stays refused until the referrer re-pins, recording
the target's current blob (0003 Q4).

### 11.10 Resolution reasons

A refused anchor or transclusion renders `#REF!(reason)` with one of these
reasons. They are resolution outcomes, not refusals of a document, so they
are not in §9's list.

| reason | applies when |
| --- | --- |
| `document-missing` | the notes directory's document, or a transclusion's target, does not exist |
| `base-unavailable` | the `base` blob, or a pin's blob, cannot be read |
| `not-in-profile` | `base`, the current text, a pinned blob or a transclusion's current target is refused under §9, a file committed with conflict markers included |
| `record-inconsistent` | §11.1's consistency rules fail, or a pinned name binds nothing in its pinned blob |
| `unaccounted-copy` | §11.4, no pair |
| `repeat` | §11.4, `EXACT` |
| `near-copy` | §11.4, `EXACT`, `MOVED` or `EDITED` |
| `refilled-gap` | §11.4, `MOVED` |
| `exact-copy` | §11.4, `EDITED` |
| `crowded-gap` | §11.4, `EDITED` |
| `span-ambiguous` | §11.5 |
| `name-rebound` | §11.9, step 3 |
| `pinned-<reason>` | §11.9, step 2 |

A transclusion whose name binds zero or several targets in the current
target renders `#REF!(name)` (§11.9, step 1).

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
  the header's width dropped.
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

- **The exact syntax of a record's frontmatter**: which YAML the anchor's
  flow mapping is read as, how its strings are quoted, and where `reply-to`
  sits. 0003 fixes the fields and the one-line rule, not the grammar.
- **How a referrer's pins are written** in its frontmatter: the key, and one
  line per target or not.
- **A table's text as one string.** §6.3 leaves per-type content to the
  suite's reading 8, which pins a table's content as rows of cells. The key
  and the similarity of §11.2 need it as one string, so this affects every
  table's correspondence and near-copy checks, not only anchors placed in a
  table.
- **Which chain, when several are longest** (§11.3, step 1). Which pairs
  are `EXACT` and which `MOVED` depends on it, so two implementations must
  pick the same one.
- **Whether the thresholds compare exactly.** Similarity is a ratio of
  integers, and a floating-point comparison at exactly 0.5 or a margin of
  exactly 0.15 can differ between implementations.
- **Whether a hit must reach the leaf's edge** when the stored `prefix` or
  `suffix` is shorter than 32 code points because the edge was nearer
  (§11.5).
- **Transclusion details**: how `path` resolves (from the referrer's
  directory, as a renderer resolves a relative link, is the reading Q5's
  reason suggests), a destination with no path, a destination in angle
  brackets, the title's other quoting forms (`'transclude'`,
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
