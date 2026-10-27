<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# The editing API — design

`blockspec.edit` changes a blockspec document for a program, so that a tool
never has to rewrite a document's lines by hand, outside the format's rules.
It has three operations, each on one **block** (`SPEC.md` §6.1, a top-level
node): replace it, insert one beside it, delete it.

This is an interface of the reference implementation, not of the format.
`SPEC.md` §2 leaves editor behaviour unspecified, so nothing here binds
another implementation, and the cases that pin it live in `tests/edit-cases/`,
not in `conformance/cases/`.

## API shape

Every operation is a pure function from text to text:

```python
from blockspec import edit

text = edit.replace_block(text, [2], "A new second paragraph.\n")
text = edit.insert_block(text, "## A new heading\n", after=[0])
text = edit.insert_block(text, "A paragraph first.\n", before=[0])
text = edit.insert_block(text, "A last paragraph.\n")
text = edit.delete_block(text, [3])
```

- `text` and each function's required arguments are positional-only (`/`).
  `before=` and `after=` are keyword-only.
- A function reads nothing and writes nothing. The caller reads the file with
  `newline=""` so line endings survive, and writes the result back. A refused
  edit raises before the caller has anything to write.
- **A block is named by its node path**, the path `parse` reports in
  `leaves` and `names`: `[i]` is the i-th block, counting from 0. A caller
  that has a name resolves it first: `parse(text).resolve("intro")["node"]`.
  A path is only good for the text it was read from. The functions take the
  text, so the path and the text cannot drift apart inside one call.
- **Only a block can be edited.** A path to a node inside a block, such as
  `[2, 1, 0]`, a paragraph in a list item, is refused as `nested-node`.
  Writing a node inside a container means writing its container prefixes,
  `>` markers and list-item indentation, and §11.7's write-back shows how
  many lines draft 0 cannot write them on. That is the answer for lists and
  block quotes: the whole list or quote can be replaced, deleted or inserted
  as one block, and nothing inside one can be. A table is edited the same
  way, as a whole block: no operation writes a cell.
- **`source` is the new block's markdown, its lines exactly.** Its lines are
  split as the reader splits lines (CRLF, CR or LF), and one final line
  ending, if present, is dropped. It must read, in place, as exactly one
  block made of exactly those lines: so it may not be empty, and may not
  start or end with a blank line. A one-line marker, `<!-- #name -->`, is a
  block, and may be inserted.
- `insert_block` takes at most one of `before=` and `after=`. With neither,
  the block goes after the document's last block, or, in a document with no
  blocks, at the end of the file.

## Where the lines go

Lines are the reader's (`SPEC.md` §3): a line ends at CRLF, CR or LF, and an
empty string after the last line ending is no line. A **blank** line holds
only spaces and tabs. Each line keeps its own line ending: no line the
operation is not about changes, byte for byte, with the one exception of the
last line of a file that has no final line ending (below).

**The line ending of a new line**, `E`: the line ending of the line directly
before the first new line, when there is such a line and it has one;
otherwise the first line ending in the file; otherwise LF.

**`replace_block`** replaces the block's lines, from its first line to its
last (the block's range, `SPEC.md` §10: it starts and ends on a non-blank
line), with `source`'s lines. Every new line but the last ends in `E`, where
the line before the first new line is the line before the block. The last
new line ends as the block's last line did, which is no line ending when the
block ended the file without one. The lines around the block, blank or not,
are kept: replace adds no blank line, so a block that sits directly against
a neighbour still does, and the read-back below refuses a result in which
that neighbour now reads differently.

**`insert_block`** inserts `source`'s lines at one point:

- `after=[i]`: directly after block `i`'s last line;
- `before=[i]`: directly before block `i`'s first line;
- neither: directly after the last block's last line, or, with no blocks,
  after the file's last line.

A blank line is added between the new block and the line before the
insertion point, when there is such a line and it is not blank; and between
the new block and the line after it, when there is such a line and it is not
blank. So the new block always has a blank line, or the file's edge, on each
side, and the lines already there are kept. A blank line added is empty, and
ends in `E`. Every new line ends in `E`, except at the end of a file that has
no final line ending: there the old last line gains `E`, and the new last
line has no line ending, so the file still ends as it did. An empty file
has no last line, so every new line in it ends in `E`, which is LF there.
Frontmatter's
closing `---` is a non-blank line like any other.

**`delete_block`** removes the block's lines, from its first to its last,
and one run of blank lines beside it:

- when a non-blank line follows the block, the blank lines between the
  block's last line and that line;
- otherwise, the blank lines between the block's first line and the
  non-blank line before it, or the start of the file.

Blank lines after the document's last block, at the end of the file, are
kept. When the file has no final line ending and the lines removed include
its last line, the new last line loses its line ending. (That line is never
blank: the blank run before the block was removed with it.) When the line
left before those kept blank lines ends in a bare CR and the first of them is
empty and ends in LF, the two endings read as one CRLF, so that blank line is
gone: no bytes can hold a bare CR followed by an empty LF line. A document whose
only block is deleted keeps its frontmatter and the blank lines after the
block, if it had any, and is otherwise empty.

The resulting shapes, for a block of `n` lines and a source of `m`:

| operation | lines |
| --- | --- |
| `replace_block` | `n` removed, `m` added |
| `insert_block` | `m` added, and up to 2 blank lines; at the end of a file with no final line ending, 1 more changed |
| `delete_block` | `n` removed, and the blank lines beside it |

## Refusal rules

An edit is refused, with nothing returned, in four ways. Each raises
`blockspec.Refusal`, whose `code` names the refusal. `blockspec.edit.EditRefused`
is the subclass for the API's own reasons. No API reason is spelled like a
`SPEC.md` §9 identifier, so the two never collide.

Arguments are type-checked first (below), then:

1. **The input is refused.** A document `SPEC.md` refuses is not edited. The
   refusal is the input's own, with its §9 identifier.
2. **The request cannot be written.** Checked before any text is built, in
   this order:
   - `bad-position`: `insert_block` given both `before=` and `after=`;
   - `no-such-block`: the path names no node of the document. `[]` is the
     document itself, not a block, and is refused this way too;
   - `nested-node`: the path names a node inside a block (above).
3. **The result is refused.** The new text is read in full, so every §9
   refusal applies to it, and the error carries that refusal's identifier:
   a marker the edit leaves naming nothing is `dangling-marker`, one half of
   a region deleted is `unpaired-region`, a name inserted twice is
   `duplicate-name`, a table put directly against a line is
   `table-not-blank-above` or `table-not-blank-below`, a source the profile
   refuses, such as a setext heading, is that source's refusal.
4. **The result does not say what was asked.** The new text is read back
   and compared with the old, block by block. In this order:
   - `not-one-block`: after `replace_block` or `insert_block`, the new
     lines are not exactly one block of the result. The source is empty,
     starts or ends with a blank line, holds more than one block, or reads
     into a neighbour: a list item beside a list of the same kind joins it,
     an unclosed fence takes in the rest of the document, a line indented
     under a list item continues it, a `---` pair at the top of the file
     becomes frontmatter.
   - `changes-another-block`: a block the edit was not about no longer reads
     as it did: its type, its number of lines or its leaves (each leaf's path
     inside the block, type and content) differ, the document has a block
     more or fewer than the edit makes, or the frontmatter differs. Deleting
     a paragraph between two lists of one kind joins them, and is refused
     this way.
   - `rebinds-name`: a name binds to something other than it did. A
     one-line marker names the next node (`SPEC.md` §7.2), so inserting a
     block directly after one, or deleting the block one names, while the
     marker stays, would move the name to another block. A name declared by
     a marker in the block replaced or deleted may go, and a name declared
     by the new block may appear. A name bound to the block replaced, or a
     region holding it, stays bound to the block in its place, whatever its
     type. A region may lose the block deleted, and
     gain the block inserted between its markers: that is what inserting
     into a region means. Nothing else about any name may change. Heading
     slugs are not compared: they are resolvable, not durable (§8.3).

   The check exists so that a gap in the placement rules above is a refusal
   rather than a wrong file.

A replacement whose lines equal the block's, compared without their line
endings, returns the text unchanged.

Arguments of the wrong type raise `TypeError`, not a refusal: `text` and
`source` must be `str`, and a path a list or tuple of `int`s.

## What the API does not change

**Records are never touched.** No function reads or writes a `<doc>.notes/`
directory. An edit can change how a record resolves under §11, from
`RESOLVED` to `EDITED`, `MOVED` or `ORPHANED`; re-anchoring a record
(§11.1) is the anchor code's work, done against the new text, and not this
API's.

The API adds functions. It does not change `SPEC.md`, the reader or the
anchor resolver.
