<!-- SPDX-License-Identifier: CC0-1.0 -->
# The fixture tree

CC0. Copy it into any implementation, in any language. Everything a runner
needs is in the files.

This tree was written before any blockspec implementation existed. It encodes
draft 0 as `docs/adjudications/0001-syntax.md` and `0002-block.md` state it
(each section's *What draft 0 carries*). There was no `SPEC.md` then. Where the
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

The cases listed at the end of this paragraph were added later, against
blockspec `926d7a1`, after an implementation existed on an unmerged branch
(`feat/reference-parser`, kindspec/blockspec#37). Their author did not read
that implementation, its tests or its mutation gate. They had what the first
author had, with this tree at `926d7a1` in place of rowspec's, plus
CommonMark 0.31.2's `spec.txt` (tag `0.31.2`), the GFM spec's tables
section, and #37's description, which lists inputs the tree did not pin
without saying what each should produce. Each expected outcome comes from
the adjudications, the readings below or the cited spec passage, and was
cross-checked against pandoc 3.1.11.1 (`-f commonmark`, `-f gfm`) and
markdown-it-py 3.0.0 (`commonmark` preset, tables enabled); a WHY.md
says where one of them disagrees with the spec. The cases:
`frontmatter/the-first-of-two-closing-lines-ends-it`,
`refusal/setext-heading/refuses-a-closing-line-with-trailing-spaces` (since
moved, below),
`partition/item-content-indent-counts-the-spaces-after-the-marker`,
`partition/a-list-marker-needs-a-space-after-it`,
`partition/an-ordered-item-must-start-at-one-to-interrupt-a-paragraph`,
`partition/an-empty-item-does-not-interrupt-a-paragraph`,
`leaf/tab-in-an-item-reaches-the-content-column`,
`leaf/heading-trailing-spaces-are-stripped`,
`leaf/fence-indent-is-removed-up-to-its-width`,
`leaf/a-shorter-fence-is-content`,
`leaf/the-other-fence-character-is-content`,
`refusal/link-reference-definition/accepts-text-after-the-destination`,
`refusal/raw-html/refuses-a-marker-with-text-after-it`,
`table/a-header-wider-than-the-delimiter-row-is-not-a-table`,
`refusal/duplicate-name/refuses-a-name-begun-twice`.

The same author added a second set later, against the owner's rulings of
2026-10-14: the addenda to 0001 and 0002 (the marker line, heading slugs,
markers that name nothing, three defaults, and `ambiguous-table`), read
from #37's branch before they reached `main`, with the schema's eleventh
refusal code taken from the same branch. The
implementation, its tests and its mutation gate stayed unread, and the
same two second opinions were used. The cases:
`frontmatter/dots-do-not-close-it`,
`name/marker-spacing-is-free`,
`refusal/ambiguous-table/accepts-a-one-cell-table-with-a-piped-header`,
`refusal/ambiguous-table/accepts-a-pipeless-line-over-two-cells-in-a-quote`,
`refusal/ambiguous-table/accepts-a-pipeless-line-over-two-cells`,
`refusal/ambiguous-table/refuses-a-pipeless-header-over-one-cell`,
`refusal/ambiguous-table/refuses-after-a-paragraph-line`,
`refusal/ambiguous-table/refuses-inside-a-block-quote`,
`refusal/ambiguous-table/refuses-inside-a-list-item`,
`refusal/dangling-marker/refuses-a-marker-before-a-marker`,
`refusal/dangling-marker/refuses-a-marker-before-a-region-begin`,
`refusal/dangling-marker/refuses-an-empty-region`,
`refusal/duplicate-name/refuses-a-second-begin-with-one-end`,
`refusal/raw-html/refuses-an-unknown-marker-suffix`,
`refusal/raw-html/refuses-an-upper-case-marker-name`,
`refusal/table-not-blank-below/refuses-a-pipe-only-line-below`,
`refusal/table-not-blank-below/refuses-a-space-and-pipe-line-below`,
`resolve/duplicate-slug-across-depths-is-ref`,
`resolve/slug-drops-punctuation`,
`resolve/slug-is-lower-cased`,
`resolve/slug-keeps-runs-of-hyphens`,
`resolve/slug-keeps-each-of-two-spaces`,
`resolve/slug-keeps-underscore` (since renamed, below),
`resolve/slug-of-a-nested-heading`,
`table/a-dash-delimiter-row-is-a-list-item`.

Later the 0001 addendum was rewritten (slugs over a heading's raw content
by github-slugger 2.0.0's own character class, no slug for a heading
holding `*`, `_`, a backtick, `[` or `<`, and marker spacing limited to
spaces and tabs). The existing expectations still hold, and the WHY.md files
that quoted the earlier wording now quote the rewritten one. Slugs were checked with
github-slugger 2.0.0's `slug()` under Node. Added then:
`resolve/a-heading-with-inline-markup-has-no-slug`,
`resolve/a-heading-with-inline-markup-shares-no-slug`,
`resolve/slug-drops-a-superscript-digit`,
`refusal/raw-html/refuses-a-marker-spaced-with-a-no-break-space`,
`refusal/raw-html/accepts-a-tab-spaced-marker`.

After an independent review of these sets and two more rulings of
2026-10-14 (a closing `---` may carry trailing spaces or tabs, and `&`
joins the no-slug characters), one case changed and two were renamed.
`refusal/setext-heading/refuses-a-closing-line-with-trailing-spaces`
became `frontmatter/a-closing-line-may-have-trailing-spaces`, and its
expectation went from a refusal to frontmatter on lines 1 to 3.
`resolve/slug-keeps-underscore` became
`resolve/a-heading-with-an-underscore-has-no-slug`, with its expectations
unchanged. `check_tree.py` now accepts trailing spaces or tabs on a
frontmatter closing line. Added then:
`resolve/a-heading-with-a-backtick-has-no-slug`,
`resolve/plain-heading-slug-for-the-backtick-case`,
`resolve/a-heading-with-a-bracket-has-no-slug`,
`resolve/plain-heading-slug-for-the-bracket-case`,
`resolve/a-heading-with-an-angle-bracket-has-no-slug`,
`resolve/plain-heading-slug-for-the-angle-bracket-case`,
`resolve/a-heading-with-an-ampersand-has-no-slug`,
`resolve/plain-heading-slug-for-the-ampersand-case`,
`refusal/ambiguous-table/refuses-an-escaped-pipe-header`,
`table/two-pipe-only-lines-are-a-paragraph`,
`table/pipe-only-lines-then-text-are-a-paragraph`,
`frontmatter/a-closing-line-may-have-a-trailing-tab`.

When both rulings reached the 0001 and 0002 addenda, the WHY.md files that
cited them as the owner's rulings were re-pointed to the addenda, quoting
them. Added then: `frontmatter/a-no-break-space-does-not-close-it`,
`frontmatter/a-form-feed-does-not-close-it`.

The owner widened `ambiguous-table` on 2026-10-15 (0002, addendum on
ambiguous tables) to every paragraph's last line and line under it that
GitHub reads as a table header and delimiter row and pandoc and
markdown-it do not both read as one, pipe-less delimiter rows and form
feeds or vertical tabs in a delimiter row among them. That made
`frontmatter/a-form-feed-does-not-close-it` (`---`, `a: 1`, `---` and a
form feed, `Text.`) wrong: lines 2 and 3 are now that shape, and `Text.`
is a non-blank line under it, so both `ambiguous-table` and
`table-not-blank-below` apply, an order the addenda do not fix. No single
code is right, so the case was removed, and
`frontmatter/a-form-feed-does-not-close-it-before-a-piped-line`, whose
line 2 holds a pipe, keeps the form feed pinned. Added then:
`frontmatter/a-form-feed-does-not-close-it-before-a-piped-line`,
`refusal/ambiguous-table/accepts-a-lazy-dash-line-with-a-form-feed`,
`refusal/ambiguous-table/accepts-a-piped-header-over-a-piped-aligned-delimiter`,
`refusal/ambiguous-table/accepts-a-pipeless-line-over-a-two-cell-aligned-delimiter`,
`refusal/ambiguous-table/refuses-a-centred-pipeless-delimiter`,
`refusal/ambiguous-table/refuses-a-dash-delimiter-with-a-form-feed`,
`refusal/ambiguous-table/refuses-a-dash-delimiter-with-a-vertical-tab`,
`refusal/ambiguous-table/refuses-a-left-aligned-pipeless-delimiter`,
`refusal/ambiguous-table/refuses-a-piped-header-over-a-pipeless-delimiter`,
`refusal/ambiguous-table/refuses-a-pipeless-delimiter-in-a-block-quote`,
`refusal/ambiguous-table/refuses-a-pipeless-delimiter-in-a-list-item`,
`refusal/ambiguous-table/refuses-a-right-aligned-pipeless-delimiter`,
`refusal/ambiguous-table/refuses-a-two-cell-delimiter-with-a-form-feed`,
`refusal/setext-heading/refuses-an-opening-line-with-a-trailing-space`.

Further cases from the same widened addendum: a form feed or vertical tab
inside or before a delimiter cell, and the shapes it says are tried first
or are no table to any reader (a setext underline with trailing spaces or
tabs, a list item, a no-break space, a one-cell header over two cells).
Added then:
`refusal/ambiguous-table/accepts-a-dash-line-with-a-no-break-space`,
`refusal/ambiguous-table/accepts-a-list-item-line-with-a-form-feed`,
`refusal/ambiguous-table/accepts-a-one-cell-header-over-two-cells-with-a-form-feed`,
`refusal/ambiguous-table/refuses-a-form-feed-inside-a-piped-delimiter`,
`refusal/ambiguous-table/refuses-a-leading-form-feed-delimiter`,
`refusal/ambiguous-table/refuses-a-leading-vertical-tab-delimiter`,
`refusal/setext-heading/refuses-an-underline-with-a-trailing-space`,
`refusal/setext-heading/refuses-an-underline-with-a-trailing-tab`.

The owner then rewrote the ambiguous-table addendum (2026-10-15): a form
feed or vertical tab in either line of a delimiter line and the paragraph
line over it refuses them whatever the header holds, the two lines are
judged without the line above, and a lazy header line is read as it
stands. Every ambiguous-table WHY.md now quotes the rewritten text.
`refusal/ambiguous-table/accepts-a-one-cell-header-over-two-cells-with-a-form-feed`
became `refusal/ambiguous-table/refuses-a-one-cell-header-over-two-cells-with-a-form-feed`,
its expectation going from a paragraph to `ambiguous-table`.
`frontmatter/a-form-feed-does-not-close-it-before-a-piped-line` was
removed: under the rewrite its line 2 over the form-feed line is
`ambiguous-table` whatever line 2 holds, and the `Text.` line under them
makes `table-not-blank-below` arguable too, an order the addenda do not
fix. Any paragraph line over a `---` and form-feed line now meets the
table rule, so `frontmatter/a-form-feed-does-not-close-it-after-a-heading`
puts a heading there instead. Added then:
`frontmatter/a-form-feed-does-not-close-it-after-a-heading`,
`refusal/ambiguous-table/accepts-a-form-feed-line-after-a-heading`,
`refusal/ambiguous-table/accepts-a-piped-header-with-no-form-feed`,
`refusal/ambiguous-table/refuses-a-form-feed-delimiter-under-a-longer-paragraph`,
`refusal/ambiguous-table/refuses-a-form-feed-in-the-header-line`,
`refusal/table-not-blank-above/accepts-a-lazy-header-over-a-one-cell-delimiter`,
`refusal/table-not-blank-above/refuses-a-lazy-header-over-a-two-cell-delimiter`.

## Shape

The tree follows kindkit's case-tree convention (kindspec/kindkit
`case-tree/CASE-TREE.md`):

    cases/<group>/<case-name>/
        expect.json     what to assert  (required; its presence IS the case)
        input.md        the document under test, exact bytes
        WHY.md          prose, ignored by the runner

    cases/refusal/<refusal-code>/<case-name>/
        the refusal cases for one code, and their controls

An `anchor` case holds a repository instead of `input.md`; *The kind
`anchor`*, below, gives its files.

`case-body.schema.json` declares the shape of every `expect.json`. kindkit's
`tools/validate_case_tree.py` applies it.

## The kind `parse`

A case with `"kind": "parse"` asserts how one document reads. The
implementation reads `input.md` and either refuses it or returns its
structure.

| field | when | what it asserts |
| --- | --- | --- |
| `accept` | always | `true`: the document is in the profile. `false`: it is refused |
| `refusal` | `accept` is `false` | the one refusal that applies, by code (below) |
| `controls` | `accept` is `false` | ids of accepting cases on the other side of the line this refusal draws. Not an assertion about the implementation; `check_tree.py` checks they exist and accept |
| `frontmatter` | optional, `accept` is `true` | the frontmatter's line range. Absent means the document has none |
| `blocks` | `accept` is `true` | every block, in order: `type` and `lines` |
| `leaves` | `accept` is `true` | every leaf, in document order: `node`, `type` and `content` |
| `names` | `accept` is `true` | every name a marker declares, and what it binds to. `{}` when there are none |
| `resolve` | optional | names to look up, and what each resolves to |

All of `blocks`, `leaves` and `names` are compared whole: a missing or extra
entry fails the case. `frontmatter` is compared on every accepting case, so an
implementation reports none (absent or `null`) where the case has none.
`resolve` is compared for the names it lists.

### Frontmatter

Decided by the owner on 2026-10-14 (0002, *Addendum*): a leading YAML block,
opened by `---` on line 1 and closed by `---`, is opaque metadata. It is not a
block, has no leaves and takes no names. Its lines are in no block, and block
line ranges still count from line 1 of the file. As pandoc reads YAML metadata,
line 2 must not be blank: `---` followed by a blank line is a thematic break
(`frontmatter/a-blank-second-line-is-a-thematic-break`).

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
| `table` | rows of cells, header row first, as GFM's table extension splits them: each cell's inline text trimmed, with `\|` read as `|`; a body row shorter than the header padded with `""`, and cells past the header's width dropped. The delimiter row is not content |

### Names and resolution

`<!-- #name -->` binds `name` to the next sibling node in its container.
`<!-- #name:begin -->` and `<!-- #name:end -->` bind `name` to the sibling
nodes between them (0001, 0002 §3).

`resolve` tries a name against markers first, then heading slugs (0001). A
name that matches zero targets, or more than one, resolves to the string
`#REF!(name)`.

## Refusal codes

Each refusal case asserts exactly one code, and is written so that only one
refusal applies to it, or so that it combines only refusals whose order the
addenda of 2026-10-14 fix (`duplicate-name` before `unpaired-region`, both
before `dangling-marker`, and `ambiguous-table` before
`table-not-blank-above`). An implementation may word its message however it
likes; the code is what the case compares.

| code | from | refused |
| --- | --- | --- |
| `setext-heading` | 0001 | a setext heading |
| `indented-code` | 0001 | an indented code block, at any depth |
| `link-reference-definition` | 0001 | a link reference definition, at any depth |
| `raw-html` | 0001 | an HTML block that is not a region marker |
| `duplicate-name` | 0001 | one name declared twice in one document |
| `conflict-marker` | 0001 | a git conflict-marker line |
| `dangling-marker` | 0002 §3, addendum | a marker that names no node: a one-line marker with no next sibling in its container or whose next sibling is a marker, or an empty region |
| `unpaired-region` | 0002 §3 | a `:begin` and its `:end` that are not siblings in one container |
| `table-not-blank-above` | 0002 §6 | a table with a non-blank line directly above it in its container |
| `table-not-blank-below` | 0002 §6 | a table with a non-blank line directly below it in its container |
| `ambiguous-table` | 0002, addendum | a delimiter line and the paragraph line over it, judged without the line above, when either holds a form feed or vertical tab, or when they are a table candidate with no unescaped pipe in one of the two lines; at top level, in a block quote or a list item; it wins over `table-not-blank-above` |

When `duplicate-name` and `unpaired-region` both apply, the code is
`duplicate-name` (0002, addendum).

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
7. **Slugs are GitHub's, over the heading's raw content.** Draft 0 named no
   slug algorithm, so the first `resolve/` cases use headings whose text is
   one lower-case ASCII word, where every algorithm agrees. The owner has
   since decided it (0001, addendum: github-slugger 2.0.0's character class,
   at any depth, no `-1` suffix, and no slug for a heading whose raw content
   holds `*`, `_`, a backtick, `[`, `<` or `&`), and later cases test where
   slug algorithms disagree: the `resolve/slug-*` cases,
   `resolve/duplicate-slug-across-depths-is-ref`, and the no-slug cases
   `resolve/a-heading-with-inline-markup-has-no-slug`,
   `resolve/a-heading-with-inline-markup-shares-no-slug`,
   `resolve/a-heading-with-an-underscore-has-no-slug`,
   `resolve/a-heading-with-a-backtick-has-no-slug`,
   `resolve/a-heading-with-a-bracket-has-no-slug`,
   `resolve/a-heading-with-an-angle-bracket-has-no-slug` and
   `resolve/a-heading-with-an-ampersand-has-no-slug`, each with a
   `resolve/plain-heading-slug-for-the-*-case` control.
8. **Leaf content, as tabled above.** 0002 says "parsed content, with
   container prefixes removed". The table pins what that is per type: a
   paragraph's and a heading's raw inline text, a code or HTML block's lines,
   and a table's cells, `table/cell-escapes-and-row-widths` among them.
9. **Frontmatter ends at the first later line that is `---`, optionally
   followed by spaces or tabs**, and may be empty (`---` on lines 1 and 2).
   `frontmatter/the-first-closing-line-ends-it`,
   `frontmatter/the-first-of-two-closing-lines-ends-it`, `frontmatter/empty`,
   `frontmatter/a-closing-line-may-have-trailing-spaces`,
   `frontmatter/a-closing-line-may-have-a-trailing-tab`. Other whitespace
   after the `---`, such as a no-break space or a form feed, does not close
   it: `frontmatter/a-no-break-space-does-not-close-it`,
   `frontmatter/a-form-feed-does-not-close-it-after-a-heading`. The
   opening line is exactly `---`
   (`refusal/setext-heading/refuses-an-opening-line-with-a-trailing-space`).
   This reading first
   said "exactly `---`", called that the narrower reading, and said relaxing
   it later was lossless. It was not: under "exactly", the document
   `---\na: 1\n---  \nText.\n\n---\n` closes its frontmatter on line 6 and
   swallows the paragraph, so the relaxed reading changes an accepted
   document's structure. The owner ruled on 2026-10-14 for pandoc's
   reading, trailing spaces or tabs allowed. Line 2 must not be blank
   (decided, below), so a document that opens with a thematic break and a blank line is not
   frontmatter, whatever `---` lines come later.
10. **No blank line is needed after frontmatter.**
    `frontmatter/then-a-paragraph-directly`.
11. **Frontmatter with no closing `---` is not frontmatter**, and its lines
    parse under the existing rules, so the document is not refused for it.
    `---` anywhere but line 1 is likewise a thematic break or a setext
    underline. `frontmatter/unclosed-is-not-frontmatter`,
    `refusal/setext-heading/refuses-frontmatter-not-on-line-one`.
12. **Frontmatter is opaque to the block rules but not to the conflict-marker
    scan**, which 0001 §4 runs before any parsing.
    `frontmatter/hides-what-the-profile-refuses`,
    `frontmatter/hides-a-marker`,
    `refusal/conflict-marker/refuses-inside-frontmatter`.
13. **Frontmatter content is not checked as YAML.** Opaque means unparsed, so
    text that is not valid YAML is still frontmatter, and nothing in it is
    refused but a conflict-marker line.
    `frontmatter/the-first-closing-line-ends-it`, `frontmatter/hides-a-marker`,
    `refusal/conflict-marker/refuses-inside-frontmatter`.
14. **A conflict-marker line is a column-0 run of seven or more `<`, `>` or
    `|` followed by a space or the end of the line, or of seven or more `=`
    alone on its line.** D8 §7.2 says git emits runs of "7-or-more". A run of `=` with
    other text after it is not a marker.
    `refusal/conflict-marker/refuses-an-eight-character-run`,
    `accepts-a-separator-run-with-trailing-text`.

## Not pinned yet

Questions the adjudications leave open, with no case in this tree, because
any case would decide them:

- **CRLF line endings.** The owner has decided that leaf content uses `\n`
  everywhere (0002, addendum), but no fixture has CRLF bytes yet. The
  repository's `.gitattributes` already exempts this tree from line-ending
  normalisation (`conformance/cases/** -text`), so a CRLF fixture keeps its
  bytes.

The marker after a marker, the empty region, the marker line grammar,
frontmatter closed by `...` and the slug algorithm were listed here until
the owner decided them on 2026-10-14 (0001 and 0002, addenda); each now has
cases.

## The kind `anchor`

A case with `"kind": "anchor"` asserts how comments, suggestions and
transclusions resolve, as `SPEC.md` §11 decides them
(`docs/adjudications/0003-anchors.md` and its addendum). The case directory
holds a small repository: the current snapshot, the earlier blobs it can
still read, and, optionally, a merge that produces part of the current
snapshot. The case lists records and referrers, and the outcome expected for
each.

This kind was added before any anchor case and before any implementation of
§11 existed. Its case author is to work from `SPEC.md`, 0003 and this
section, without reading an implementation.

**Landing order.** The reference reader has no `resolve` until the resolver
lands, so the first anchor case would turn `just conform` red on `main`. The
cases are therefore written blind from `main`, on a branch and pull request of
their own, and reviewed there. The resolver's branch is then rebased onto the
cases, run against them with no case changed, reviewed, and merged: that merge
lands the cases and the resolver together, and the cases' pull request closes
as landed through it.

### Files

    cases/anchor/<group>/<case-name>/
        expect.json         what to assert
        WHY.md              prose, ignored
        tree/<path>         the current snapshot: each file of the repository, at its path
        blobs/<any name>    more blobs the repository can read, such as a record's base
        merge/base/<path>   the three sides of a merge whose result is tree path <path>
        merge/ours/<path>
        merge/theirs/<path>
        <anything else>     not in the repository: a placeholder's target, a written file

Every file is exact bytes, as everywhere in this tree, so a CRLF or a bare CR
in a fixture is kept.

**The repository.** Its files are those under `tree/`, at their paths below
`tree/`, plus each merge's result. Its readable blobs are every file under
`tree/`, `blobs/` and `merge/`, and each merge's result. A file anywhere else
in the case directory is in neither: it can still be named by a placeholder,
and the blob it names is then one the repository cannot read, which is how a
case sets up `base-unavailable` (§11.11's squash-merge, for example). A file
under `blobs/` is readable and in no path of the current tree, which is how a
case gives a `base` that an earlier commit held.

**Ids are content-addressed.** An unreadable file with the same bytes as a
readable one names a readable blob, so the case would not test what it
means to. `check_tree.py` reports a placeholder target outside `tree/`,
`blobs/` and `merge/` whose bytes equal a readable file's; give such a file
bytes of its own.

**Placeholders.** `{{blob:PATH}}`, anywhere in any file of the case, is
replaced by the object id of the file at `PATH`, a path relative to the case
directory, as `git hash-object` computes it over that file's exact bytes, in
lower-case hex. Write it where a record's `base` or a pin's `blob` goes, so
that a case holds content and never a hash:

    anchor: {"base": "{{blob:blobs/policy.md}}", "leaf": {...}, ...}

The file a placeholder names must not hold a placeholder itself. Placeholders
are replaced before anything else happens, in merge sides and written files
too. A literal id needs none: write one to pin a malformed `base`, or the id
of a blob that no file of the case has.

**`object_format`**, optional: `"sha1"`, the default, or `"sha256"`. Ids are
computed in a repository of that format, and it is the format §11.1's `B`
is checked against: 40 hex digits for SHA-1, 64 for SHA-256.

**`merge`**, optional: an object from a repository path to `"clean"` or
`"conflict"`. For each path, the runner commits `merge/base/<path>`, commits
`merge/ours/<path>` on one branch and `merge/theirs/<path>` on another, and
runs a stock `git merge` of each into the base, ours first, with no
configuration from the machine (kindkit `gitmerge.merge`). Stock git, since
correctness may not depend on a merge driver (0003 §1). The working-tree
text afterwards is the current file at `<path>`, with its conflict markers
when there are any; they are labelled `<<<<<<< HEAD` and `>>>>>>> b1`, and in
a file whose lines end in CRLF git ends the marker lines in CRLF too. The
case fails if git's outcome is not the one stated. `tree/<path>` must not
exist as well. Each merge is of one file; a record is added on a branch by
putting it straight into `tree/`, where git would have merged it cleanly.

### What a case asserts

| field | when | what it asserts |
| --- | --- | --- |
| `object_format` | optional | above |
| `merge` | optional | above |
| `records` | at least one of the two | for each record named, by its path in the repository, its outcome (below) |
| `transclusions` | at least one of the two | for each referrer named, by its path in the repository, every transclusion in it, in document order (below) |
| `controls` | when any outcome is `REFUSED(...)` | ids of `anchor` cases on the other side of the line the refusal draws, as for a `parse` refusal. Not an assertion about the implementation; `check_tree.py` checks they exist and are `anchor` cases |

A record's path is `<document>.notes/<file>` (§11.1), so the document it
belongs to is the path with `.notes/<file>` removed. Each record and referrer
named must be a file of the current snapshot. Records and referrers the case
does not name are not compared.

**A record's outcome** has four fields, all required:

| field | value |
| --- | --- |
| `status` | `RESOLVED`, `MOVED`, `EDITED`, `DETACHED`, `ORPHANED` or `REFUSED(<reason>)`, with a reason from §11.10's table (§11.6). For a reply (§11.1, §11.8): `REPLY` when its `reply-to` names a record in its directory, `#REF!(reply-to)` when it does not. `REPLY` is this tree's word for a reply that renders normally, not a §11.6 status. A reply refused for its frontmatter is `REFUSED(record-inconsistent)` |
| `leaf` | the current leaf the anchor is on, `{"node": path, "type": type}`, with `node` as *Nodes and paths* above, over the current document, and `type` one of `paragraph`, `heading`, `code_block` and `table`. The paired leaf for `RESOLVED`, `MOVED`, `EDITED` and `DETACHED` (§11.6: `DETACHED` renders on it); `null` for every other status |
| `span` | `[start, end]`, the span's code point offsets in that leaf's text as §11 defines it (§6.3's content, NFC, `\n` line endings; a table's text as §11.2 builds it), start inclusive and end exclusive. Given for `RESOLVED`, `MOVED` and `EDITED`; `null` otherwise |
| `suggestion` | `null` unless the record's frontmatter holds the line `kind: suggestion`, exactly. Otherwise §11.7's gate: `{"gate": "apply", "written": FILE}` when the suggestion applies, or `{"gate": "stale", "reason": R}` when it does not |

For `"gate": "apply"`, `FILE` is a path relative to the case directory, such
as `written/policy.md`, and holds the exact bytes of the current document
after §11.7's write-back of `replace` (its steps 1 to 3). Only the document
is compared; the record's own `status: accepted` is not. `apply` is only
possible with `RESOLVED` or `EDITED`. For `"gate": "stale"`, `R` is
`"unmappable-offset"` when the record's `status` is `open`, its anchor is
`RESOLVED` or `EDITED`, and the span does not map (§11.7); it is `null` for
every other stale suggestion, whatever made it stale.

**A transclusion's outcome** has three fields, all required. The list holds
one per transclusion paragraph (§11.9) of the referrer, in document order,
and `[]` for a referrer with none:

| field | value |
| --- | --- |
| `leaf` | the transclusion paragraph, `{"node": path, "type": "paragraph"}`, over the referrer |
| `status` | `RESOLVED`; `REFUSED(<reason>)` with a reason from §11.10's table, `pinned-<reason>` written out (`REFUSED(pinned-orphaned)`, `REFUSED(pinned-near-copy)`); or, for §11.9's step 1, `#REF!(<name>)` with the name as the destination writes it after its `#`, as `resolve` writes it for a `parse` case |
| `unit` | for `RESOLVED`, what is transcluded: `{"document": path, "target": target}`, where `path` is the target document's path in the repository, after §11.9 resolves the link's path from the referrer's directory, and `target` is what the name binds in the current target, written as `names` writes it (a node, or `{"region": [...]}`). `null` for every other status |

Each listed record and each listed referrer's list is compared whole: a
field that differs, or a transclusion missing or extra, fails the case. An
implementation may add fields of its own, such as a message, and they are
ignored. A path index or an offset must be an integer, not a float or a
bool.

**One outcome per record.** §11.10, *Which reason is reported*, fixes the
order among a record's or a transclusion's input problems, and among several
`pinned-<reason>`s. §11.4 fixes an order inside each kind of pair ("the
first rule that applies decides"), and §11.9 orders its steps. Where one of
these orders applies, a case may set up several reasons and expect the first
by that order; §11.10's order needs such cases to be pinned at all. To pin
one reason on its own, a case where only that reason applies is still the
clearest. Where `SPEC.md` fixes no order between two reasons, write the case
so that only one applies, as a `parse` refusal case does (§9).

### An example

Shown for the shape, not as a case of this tree. `policy.md` is unchanged
since the comment was made, so `base` is the blob of the current file:

    tree/policy.md
        The scram threshold is 4.2 sigma.
    tree/policy.md.notes/01J9Z3M8Q4X7V2K6T0R5N1B8CD.md
        ---
        anchor: {"base": "{{blob:tree/policy.md}}", "leaf": {"type": "p", "nth": 0, "text": "The scram threshold is 4.2 sigma."}, "span": "4.2 sigma", "prefix": "The scram threshold is ", "suffix": "."}
        kind: comment
        status: open
        ---

        Still right?

    expect.json
        {
          "kind": "anchor",
          "records": {
            "policy.md.notes/01J9Z3M8Q4X7V2K6T0R5N1B8CD.md": {
              "status": "RESOLVED",
              "leaf": {"node": [0], "type": "paragraph"},
              "span": [23, 32],
              "suggestion": null
            }
          }
        }

### What an implementation is handed

`run_cases.py`'s docstring gives the interface: `resolve(repo, queries)`,
where `repo` is `{"object_format", "tree", "blobs"}` (each current file's
text by its path, and each readable blob's text by its object id) and
`queries` is `{"records": [...], "transclusions": [...]}`, the paths the
case names. The implementation needs no git: the runner has already hashed
the blobs and run the merges.

### What this kind cannot express

- §11.8's warning for a record id in two notes directories, and what a
  validator reports for a rename: no field asserts a warning.
- How a status renders, beyond the fields above (the base text beside a
  loud status, for one).
- Bytes that are not UTF-8, a symbolic link, a submodule and an empty
  directory: every fixture is a UTF-8 file.
- A merge of more than one file in one repository, or a rename.
- What a tool writes: a re-anchored record (§11.1), the creation of a new
  anchor, including the refusal to create one when `prefix + span + suffix`
  does not occur exactly once, and a referrer's re-pin (§11.9). A case asserts
  how existing records and pins resolve, not what a tool would write.

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
