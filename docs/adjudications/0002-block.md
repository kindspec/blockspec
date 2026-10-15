<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Adjudication 0002: what is a block?

blockspec#4. The brief (`DESIGN-BRIEF.md` §2) lists it as open: *"Paragraph?
Any top-level node? Does a list count as one block or many?"* The issue calls
it partly empirical. Uniqueness under each candidate definition was measured
first, in kindspec/research `experiments/D8-block-definitions/` (PR #17). Whether
a list is one block or many is a modelling choice, so the org contract
(kindspec/.github `AGENTS.md` §4, "When measurement cannot settle it") has one
case argued for each side from the same evidence, and an adjudication written
here. The format follows kindspec/research `design-findings/ADJUDICATION.md`
and adjudication 0001.

The two positions, each committed as argued, with these edits only: an SPDX
header; paths to scripts and output that pointed at working files now point
at kindspec/research `experiments/D8-block-anchoring/cases/`, and one output
file was renamed to match; local clone paths and a branch name were dropped;
the research pin moved from `8b9c33c` to `b292907`, the squash merge of the
same PR, in which only the `d2` rows of `results.txt` differ; one process
sentence and one "(ad hoc; not saved)" note were reworded; the top-level
case's title was split and long lines were wrapped; and three quoted
procedure steps from obsidian-help, which carries no licence, are
paraphrased.

- **top-level** ([`0002-block/top-level-case.md`](0002-block/top-level-case.md)):
  a block is a top-level CommonMark node, and a list is one block. It concedes
  that stage 1 of a comment anchor should resolve the list item, not the list.
- **leaf** ([`0002-block/leaf-case.md`](0002-block/leaf-case.md)): a block
  is a leaf node at any depth (paragraph, heading, code block, HTML block,
  table, thematic break), and lists, items and block quotes are containers.

Both cases ended at the same hybrid: (b) as the unit, with the anchor going to
something smaller inside a list. They disagreed on what that smaller thing
is, and on whether the rest of the design should follow it. This document
answers that per job.

Pins: blockspec `3a1544a`. kindspec/research `b292907` (main, with #17), and
the new measurement in `experiments/D8-block-anchoring/` at research main
`244dff0`, the squash merge of PR #18. Its files there are byte-identical to
the PR head `18506e9`. Corpora at PRE-REGISTRATION-2 §6.2's pins, as
`D8-block-definitions/arms.json` lists them. markdown-it-py 3.0.0 (preset
`commonmark`, GFM tables enabled where stated) and pandoc 3.1.11.1 (`-f gfm`).

## Decision

**Decided, 2026-10-14.** "Block" is one thing, the unit the document is cut
into. The other jobs the word was doing address nodes of the same CommonMark
tree, and each gets the node that the evidence picks for it:

| job | the unit | the rule |
|---|---|---|
| **partition** | the **block**: a top-level node | A document is a sequence of blocks. A list is one block, and so are a block quote and a table. Every non-blank line after frontmatter is in exactly one block. |
| **anchoring**, stage 1 | the **leaf** that contains the anchored text | A leaf is a paragraph, heading, code block, HTML block, table or thematic break, at any depth. Its quote is its parsed content, with container prefixes removed. There is no fallback to the enclosing block. |
| **naming** with `<!-- #name -->` | the **next sibling node in the same container** | This is 0001's rule, unchanged, at any depth. At top level the node is a block. Inside an item or a quote it is the next node there. A marker with no next sibling is refused. |
| **naming** with `:begin` / `:end` | the **sibling nodes between the two markers** | Both markers must be siblings in one container. That is how a single list item's content is named. |
| **transclusion** | **what a name names** | One node with its subtree, or the nodes of one region. It is rendered as block content in the referrer. |
| **conformance tree** | **the partition plus the leaves** | Each case pins every block (type, line range) and every leaf (type, content), and which node each name binds to. |

**GFM pipe tables are in the profile** as a leaf block, from the GFM spec's
"Tables (extension)" section (0.29-gfm). Two shapes are refused: a table that
starts on the line after a paragraph line, and a table followed by a non-blank
line in the same container. A table must have a blank line, or its
container's edge, on both sides.

**What a leaf is**, used everywhere below: a paragraph, heading, code block,
HTML block, table or thematic break. Under 0001's profile an HTML block is
always a region marker, since other raw HTML is refused, and a code block is
always fenced, since indented code is refused. A marker and a thematic break
carry no text to quote, so in practice an anchor lands in a paragraph,
heading, fenced code block or table.

**No owner question remains.** The deciding question the top-level case asked,
*does blockspec need to transclude or name a single list item?*, is answered
without new syntax. A region pair placed inside the item names its content,
which the probe below confirms. Naming an item with a one-line marker would
need a new binding rule, and is listed under *What would reverse it*.

## The factual disputes, settled

Each figure the cases relied on was re-run. All re-runs used the cases' own
scripts, at the pins, from their copies in research `D8-block-anchoring/cases/`,
and every output matched the case's own. The new measurement,
`D8-block-anchoring/scope.py`, grades the anchoring question with D8's line
oracle. Neither case had run that. It is described under §2.

| claim | [top-level case](0002-block/top-level-case.md) | [leaf case](0002-block/leaf-case.md) | measured | command |
|---|---|---|---|---|
| pooled within-file duplicates, ≥40 chars, `local` column | — | (b) 0.62%, (f) 0.92% | **The arithmetic is right, and it pools two arms that must not be pooled.** Summing all seven arms gives 1,202/194,004 = 0.62% and 2,223/242,644 = 0.92%. But `D8-block-definitions/README.md` says `k8s-en` and `k8s-l10n` "are never pooled". Without `k8s-l10n` it is **0.48% against 0.69%**, and with `distinct` in place of `local` 0.53% against 0.76%. The case printed the no-l10n row too. The gap is about 0.2 points either way. | sum each column of `results.txt` "Summary, minlen=40" per definition, with and without `k8s-l10n` |
| (b) is lowest or tied, instances dup in file, in 6 of 7 arms | 6 of 7, rust-book the exception | — | **True at one decimal, 5 of 7 at full precision.** (b) is lowest in obsidian-help, k8s-l10n, cncf-toc and site-policy (0.559% against 0.618% (d) and 0.595% (f)), and all three are 0 in cmspec. In k8s-en (d) is lower, 2.140% against (b)'s 2.147%. In rust-book (b) is highest, 4.397% against 4.235% (d) and 4.137% (f). | `results.txt`, same section, dup in file / blocks per arm |
| stage-1 exact match under edits, obsidian-help and rust-book, gap 5 | — | (f) 80–82%, (b) 37–54% | **Reproduced byte for byte**: (f) 81.5% and 79.9%, (b) 54.0% and 36.7%. **It is a status count, not correctness.** `edits2.py` has no oracle. A whole list that resolves FUZZY is a high-entropy match, and D8 §3.2's silent wrongs were low-entropy. Graded by the oracle, (b)'s losses are loud refusals, not wrong answers (§2). The direction holds. The stated reason, that the fuzzy path is where silent wrongs live, does not. | `cases/leaf/edits2.py REPO PATHSPEC 5 MAXFILES`, `cases/leaf/edits2.txt` |
| loud ambiguity at rest, top-level items ≥40 chars | (d) 1.81% obsidian-help, 0.45% k8s-en, 0.27% cncf-toc; (b) 0, 0.03%, 0 | — | **Reproduced byte for byte.** It comes from narrowing stage 2, not from the list being unique. Let (b)'s stage 2 search the whole file and its refusals become (d)'s: 36 of 1,990 on obsidian-help, and 66 of 14,530 on k8s-en. The same mutation in `scope.py` moves B from 0 to 46 of 3,020 leaf anchors, F's figure. | `cases/top-level/rest.py`, with stage 2 given every item in the file; `red_states.sh`, fourth case |
| ambiguity after edits, leaf | — | AMBIGUOUS 0.0–0.3% of anchors | **Reproduced**: 0.0%, 0.2%, 0.3% at gaps 1, 5 and 25 on obsidian-help. | `cases/leaf/edits2.txt` |
| comment-on-item correctness, (b) list-then-item against (d) item, gaps 5 and 25 | (b) loses 0 to 8.3 points, all loud; silent-wrong 0 under both | — | **Reproduced byte for byte** over six arms, and a mutation showed the oracle is live. Switching (d) to the naive policy and moving 5% of its hits by one item produced 61 silent wrongs. | `cases/top-level/edit_b_vs_d.py`, `cases/top-level/edit-run.txt` |
| stored stage-1 quote | list median 208, 289, 330 chars; p90 540–1,092 | the enclosing list is a median 3.9× and p90 13.2× the anchored paragraph | **Both reproduced, and both understate it per anchor.** The top-level figure is per list. Long lists hold more anchorable text, so per anchor the list is longer. The median is 289–969 chars in five arms (2,438 in cmspec, whose 18 anchors sit in one list), against 64–122 for the leaf, which is **4.3× to 8.5×** at the median. The p90 is 716–7,200 against 147–434. | `cases/top-level/sizes.py`; `cases/leaf/edits.py`; `scope.py`, "Stored stage-1 quote" |
| the rust-book gap-25 run | — | (f) 72.2% resolves, (b) 58.7% | **It finished.** The figures in the case are from the completed run, and a re-run gives the same output. | `cases/leaf/edits2.py rust-book 'src/*.md' 25 112` |
| a column-0 marker between items, or a bullet-character change, splits a list | yes | — | **Yes**, under both markdown-it and pandoc's `gfm` reader. The same holds for a column-0 `:begin` / `:end` pair around one item, which makes three lists. | `probe.py` |
| one blank line makes every item of a list loose | yes | — | **Yes.** | `cases/top-level/probe.py` |

## 1. The partition: a top-level node

**Decided for the top-level case.**

The partition is what the document *is*: a sequence of blocks, each a run of
whole lines. It is what D8 §7.1's correspondence works on ("blocks are
boundaries plus raw bytes"). It is what a diff or a merge report talks about,
and it is the top level of every conformance case.

- **It is a true partition of the lines.** A top-level node is a contiguous
  line range, and its content is those lines, stripped. Only link reference
  definitions fell outside every top-level node in #17's corpora
  (`D8-block-definitions/README.md`, `uncovered`), and the profile already
  refuses those (0001, *What draft 0 carries*). So under the profile, every
  non-blank line after frontmatter is in exactly one block. A leaf
  definition is not a partition of lines. List markers and `>` prefixes
  belong to no leaf, which the leaf case concedes in its §4.
- **It duplicates least of the definitions that cover every node type.** At
  ≥40 characters, `local`, without `k8s-l10n`: (b) 0.48%, (d) 0.61%, (f)
  0.69%. (b2) is lower again, 0.31%, because it drops code and HTML, so it
  does not partition.
- **Its fragility does not reach the anchors.** A bullet-character change or a
  column-0 marker splits one list into two blocks. That moves the partition,
  which costs correspondence one split. It does not touch a stored anchor,
  because anchors address leaves (§2). Both splits become conformance cases.

## 2. Anchoring: the leaf

**Decided for the leaf case, by a measurement neither case ran.**

Both cases measured stage 1 inside lists, but neither graded the (b)-against-(f)
question with an oracle. The top-level case graded (b) against (d) with D8's
line oracle. The leaf case compared (b) and (f) by stage-1 status alone, and
named an oracle-graded run as the thing that would change its mind.
`D8-block-anchoring/scope.py` runs that oracle-graded comparison. It anchors a
leaf of ≥20 characters that sits inside a top-level list or block quote, in
real history at file-version gaps 5 and 25, over six arms. It resolves the
leaf four ways, all under D8's hard policy, plus a fifth discussed below, and
grades each with D8's line oracle applied to leaves:

- **B**: the top-level node, then the leaf inside it.
- **D**: the smallest list item that holds the leaf, then the leaf inside it.
  This is the hybrid the top-level case proposed.
- **F**: the leaf itself.
- **F+B**: F, falling back to B when F's exact match is ambiguous.

Correct resolution, % (loud refusals make up the rest unless a WRONG count is
given):

| arm | gap | anchors | B | D | F | F+B |
|---|---|---|---|---|---|---|
| rust-book | 5 | 491 | 93.5 | 98.6 | **99.8** | 99.8 |
| rust-book | 25 | 175 | 82.9 | 92.0 | **99.4** | 99.4 |
| obsidian-help | 5 | 1,229 | 96.2 | 98.5 | 98.8 | 99.3 |
| obsidian-help | 25 | 79 | 92.4 | 100.0 | **100.0** | 100.0 |
| cmspec | 5, 25 | 43, 32 | 100.0 | 100.0 | 100.0 | 100.0 |
| k8s-en | 5 | 190 | 98.4 | 100.0 | **100.0** | 100.0 |
| k8s-en | 25 | 40 | 97.5 | 100.0 | **100.0** | 100.0 |
| cncf-toc | 5 | 231 | 96.1, **1 WRONG** | 97.0 | 97.8 | 99.6, **1 WRONG** |
| cncf-toc | 25 | 71 | 94.4 | 100.0 | **100.0** | 100.0 |
| site-policy | 5 | 587 | 95.6 | 97.1 | **100.0** | 100.0 |

At rest, each anchor resolved against its own unchanged file, loud refusals:

| arm | anchors | B | D | F | F+B |
|---|---|---|---|---|---|
| obsidian-help | 3,020 | 0 | 47 (1.6%) | 46 (1.5%) | 0 |
| k8s-en | 19,912 | 36 (0.2%) | 98 (0.5%) | 157 (0.8%) | 36 (0.2%) |
| cncf-toc | 23,392 | 4 (0.0%) | 84 (0.4%) | 81 (0.3%) | 4 (0.0%) |
| rust-book, cmspec, site-policy | 1,332 | 0 | 0 | 0 | 0 |

No scheme made a wrong resolution at rest.

What this settles:

- **F is correct at least as often as D, and D at least as often as B, in
  every arm and gap.** F leads B by 0 to 16.5 points (rust-book gap 25), and
  every point of the difference is a loud refusal, not a wrong answer. The
  smallest enclosing item (D) is the wrong compromise. It is never better than
  the leaf, and it is 7.4 points worse at rust-book gap 25. An item with
  several paragraphs or a sub-list loses its exact match whenever any part of
  it is edited, as a list does.
- **The only silent wrong in the run came from the coarse scope.** In
  cncf-toc gap 5, a paragraph has three identical copies in the later
  version, in similar lists. F refused it as ambiguous. B fuzzy-matched the
  edited list to a list holding another copy, and returned that copy's
  paragraph, against the oracle. F+B
  inherits the same wrong, because it falls back to B exactly when F has
  correctly refused. **The fallback is a real trade, and this decision
  declines it.** F+B wins on recall: 99.6% against 97.8% in cncf-toc gap 5,
  99.3% against 98.8% in obsidian-help gap 5, and it removes every at-rest
  refusal that B does not also make (46 to 0 in obsidian-help). The cost is one
  silent wrong in 3,168 graded anchors. D8's invariant I3 puts an honest
  orphan before a confident wrong answer, so **no fallback from the leaf to
  the enclosing block.** *What would reverse it*, item 2, names the evidence
  that would bring one back.
- **The at-rest refusals are the leaf's real cost**, 0 to 1.5% of in-container
  anchors. They are the repeated procedure steps the leaf case identified
  (a step that opens the command palette, repeated in one file). They are
  loud. They are also visible when the anchor is made: the anchoring client
  resolves the anchor against `base` before it stores it, sees two matches, and can widen the context or refuse. How an
  anchor carries a disambiguator is the anchor format's question, and research
  `scope.py`'s F+Bc row measures one candidate: store the enclosing block only
  for an anchor that was already ambiguous when it was made. It clears the
  same at-rest refusals as F+B, and it makes the same wrong answer in cncf-toc
  gap 5, because that paragraph was already duplicated when it was anchored.
  In this run the enclosing block was not a safe disambiguator. Wider
  context, or a refusal at anchoring time, remains open.
- **Sidecar size favours the leaf**, as the dispute table shows: 4.3× to
  8.5× smaller at the median, per anchor.

**The leaf's quote is its parsed content.** For a paragraph inside an item,
that is the inline text with the item's indentation, any `>` prefixes and lazy
continuation handled as CommonMark defines a paragraph's content. 0001 §6
already asked for anchors to quote parsed text rather than raw bytes, so the
blocks are raw bytes and the anchors are parsed text, and each is the right
thing for its job. The leaf case estimates the conformance cost at 10 to 20
cases (nested quote in a list, lazy continuation, tabs in items). That is an
estimate, not a count.

**A selection that crosses leaves** (three bullets, two paragraphs) is a range
anchor under every definition. Both cases agree, and neither measured one.
Its format is left to the anchor work.

## 3. Naming

**0001's rule stands as written: a marker names the next sibling node.**

The top-level case argued that a list item cannot be named without a new rule.
The leaf case argued that (b) must either forbid markers inside lists or add a
second unit. Both are right about the tree, and neither conclusion follows,
because a name addresses a node, not a block. `probe.py` shows where every
placement lands:

| placement | the tree | what the name binds to |
|---|---|---|
| marker, then a list | `html_block@0 bullet_list@0` | the list, one block |
| marker first in an item | `list_item@1 html_block@2 paragraph@2` | the item's first paragraph |
| marker before a nested list, inside an item | `html_block@2 bullet_list@2` | the nested list |
| marker between items, at column 0 | `list@0 html_block@0 list@0` | the second list: the marker split the list |
| marker indented after an item's last node | `paragraph@2 html_block@2 list_item@1` | nothing: no next sibling. **Refused.** |
| `:begin` / `:end` inside one item | `list_item@1 html_block@2 paragraph@2 html_block@2` | that item's content |
| `:begin` / `:end` at column 0 around one item | `list@0 html_block@0 list@0 html_block@0 list@0` | the middle list: the pair split the list into three |

0001 wrote "names the next sibling block". Under this decision that reads
"the next sibling node", which is the binding 0001's own probe showed. So the
rule needs two conformance cases that 0001 did not list: **a marker
with no next sibling in its container is refused**, and **a `:begin` and its
`:end` must be siblings in one container**, or the pair is refused. The second
is a narrowing. Relaxing it later is lossless, because every region valid
under it stays valid.

A list item is the one node a one-line marker cannot name. The marker would
have to sit between items, and there it ends the list. That is a CommonMark
fact, not a profile choice. The region pair inside the item covers that need.

## 4. Transclusion

**A transclusion target is a name, so the unit is what the name binds to: one
node with its subtree, or the sibling nodes of one region.** D8 §8.1's R2 (the
target declares the region) already says that a referrer cannot transclude an
unnamed node.

The top-level case's strongest point, that a (b) block renders from its own
bytes and an item does not, is about the list item. In a list, *loose* or
*tight* is a property of the list, and a blank line between any two items
changes how every item renders. Under this decision the item is not a
transclusion unit. A named paragraph, taken out of a tight list, is
transcluded as a node and renders as a paragraph. Its tightness belonged to
the list it left. A named nested list carries its own looseness, computed from
its own items. A region renders as the sibling nodes it holds.

Whether a heading slug transcludes the heading or its section is not decided
here.

## 5. The conformance tree

The cases pin the partition and the leaves. Each case's expected output lists
every block (type, line range) and every leaf (type, content), plus each name
and the node it binds to. The list-specific cases follow from §1 to §4. Both
sides named them, and none is a new rule:

- a list is one block, tight and loose;
- a bullet-character change splits a list into two blocks;
- a column-0 marker or region pair between items splits a list;
- a marker with no next sibling is refused; a region pair across containers
  is refused;
- leaf content with container prefixes removed: a paragraph in an item, in a
  quote in an item, with lazy continuation, with a tab after the marker; an item
  with several paragraphs;
- the table cases of §6: a table after a blank line, in a list item, and
  without outer pipes, all admitted; a table on the line after a paragraph
  line, and a table followed by a non-blank line, both refused.

## 6. GFM tables

**Admitted, as a leaf block, with one refusal.**

0001 left this open. Under CommonMark 0.31.2 a pipe table is a paragraph.
Under GFM it is a table, and `probe.py` shows both.

- **The owner's answer to 0001 decides most of it.** A blockspec document must
  render and edit correctly in today's markdown tools. GitHub and Obsidian
  render pipe tables as tables. A profile that read them as paragraphs would
  build a different tree from the one every author sees, which is the dialect
  problem 0001 set out to avoid, from the other direction.
- **The corpora use them.** Tables of ≥40 characters appear at top level in
  six of the seven arms: 13 in rust-book, 81 in obsidian-help, 249 in
  k8s-en, 758 in k8s-l10n, 360 in cncf-toc and 6 in site-policy. None
  duplicates within its file (`results.txt`, "By type, minlen=40", `b
  top-node`).
- **Every #4 figure already assumed them.** #17 and `scope.py` both parse with
  tables enabled.
- **It is not new syntax.** Strictly, a table is a node of GFM's tree, not
  of CommonMark 0.31.2's. 0001's reversal item 2 fires only if a block
  boundary needs syntax that blockspec has to invent. A pipe table is GFM's,
  pinned by a published spec, and 0001 named it as #4's question.
- **It is not rowspec's syntax.** rowspec's `.mdtbl` is also a pipe table,
  and both the org contract and this repository's `AGENTS.md` forbid reusing
  rowspec's syntax. A table in a blockspec document is an opaque leaf. It has
  no row ids, no formula header and no key, so blockspec does not take on
  rowspec's model. Tabular data that needs identity or computation belongs in
  a rowspec file, and a document refers to it.

**The refusals.** When two mature parsers draw different trees, the profile
refuses the input, and `probe.py` finds two such shapes. `Intro.` followed on
the next line by a table is a paragraph and a table to markdown-it, and a
single paragraph to pandoc's `gfm` reader. A non-blank line directly after a
table's last row is one more table row to markdown-it, and a separate
paragraph to pandoc. So a table must have a blank line, or its container's
edge, before and after it. Cell content is opaque
inline text, like every other leaf's. The second-opinion parser 0001 proposes
for CI must then implement the extension. markdown-it-py, pandoc's `gfm`
reader and cmark-gfm do.

## 7. The cost of reversing each choice after draft 0

Common to every reversal: no authored file changes unless a marker has to
move, because nothing is written into the target (brief §1, no minted ids).
Every stored anchor carries `base`, the blob it was taken against (D8 §7.3), so
an anchor migration can re-cut its quote from git.

| choice | reversed to | cost |
|---|---|---|
| anchor at the leaf | the top-level block | **Lossless and mechanical.** The leaf's enclosing block is computable from `base`. |
| (the alternative) anchor at the block | the leaf | **Lossy.** A comment stored against a whole list does not say which item it meant. A migration would guess, and a guess is a silent wrong. |
| partition at top-level nodes | items or leaves | The spec text, the conformance tree and correspondence change. Anchors do not, since they never addressed the partition. |
| markers name nodes at any depth | top level only | Names inside containers become refusals, and authors move them or turn them into region pairs. That is a write to authored files, bounded by how rare names are (D8 §7.2: 0.34% of blocks in Obsidian's own vault). This is the one choice whose reverse is costlier than its forward. It is taken because forbidding adds a refusal and a second mechanism for the common case of naming one step. |
| region pair in one container | across containers | Lossless. |
| tables admitted | tables as paragraphs | Every anchor on a table changes its quote and refuses loudly until re-anchored, and the tree stops matching what forges render. Admitting them later instead would cost the same, plus the time in between, during which the tree disagrees with GitHub. |

## What each side got right

**The top-level case:**

- the partition must be flat and must cover every line, and only (b) does
  both;
- (b) duplicates least, and its at-rest advantage is real, though it comes
  from the narrower stage-2 search rather than the list itself;
- a list item's rendering depends on its siblings, so the item is not a
  self-contained unit;
- a one-line marker cannot name an item, and a column-0 marker splits a list;
- it conceded the anchoring half before anyone measured it, and the
  measurement agrees.

**The leaf case:**

- anchoring belongs at the leaf, and the oracle confirms it in every arm;
- the sidecar cost of storing a whole list for a comment on one bullet;
- the reversal asymmetry: leaf to block is lossless, block to leaf is not;
- a marker written inside a list item is valid CommonMark and binds to a node
  there, so names must reach below the top level;
- range anchors are needed under every definition.

**Where each overreached:** the top-level case's "lowest or tied in six of
seven arms" holds at one decimal and is five of seven at full precision. The
leaf case's headline duplicate figure pools
`k8s-l10n` with `k8s-en`, and its exact-path argument reads stage-1 status as
safety, which the oracle does not bear out. (b)'s fuzzy list matches were
loud, not wrong, except once. The top-level case's hybrid of the smallest
enclosing item is dominated by the leaf in every arm.

## What would reverse it

1. **An oracle-graded run in which leaf-scoped anchors resolve wrongly where
   block-scoped ones are right**, at a rate above the leaf's at-rest refusal
   cost. This is the leaf case's own criterion. `scope.py` found the reverse:
   the one wrong was block-scoped.
2. **Evidence that a fallback to the enclosing block is safe.** An
   oracle-graded run over more arms in which F+B, or another disambiguator,
   makes no silent wrong while keeping its recall gain. One silent wrong in
   3,168 anchors is a small sample in both directions. A disambiguator that
   never searches outside the leaf's own block, such as wider context, would
   also do.
3. **A requirement that a one-line marker name a list item.** The item would
   need a binding rule of its own, with conformance cases. The region pair
   covers the need without one.
4. **A second-opinion parser that disagrees with the reference on table
   boundaries** outside the refused shape. The profile would narrow its table
   rule further.
5. 0001's reversal items still stand, and nothing here triggers them. Every
   unit above is a CommonMark (or GFM table) node, and no typed attribute was
   needed.

## What draft 0 carries, from this decision

- **Blocks**: top-level nodes. A list, a block quote and a table are each one
  block.
- **Leaves**: paragraph, heading, code block, HTML block, table and thematic
  break at any depth, with content as CommonMark parses it. Under the profile
  an HTML block is a marker and a code block is fenced. Stage 1 of every
  anchor resolves a leaf.
- **Names**: `<!-- #name -->` binds to the next sibling node in its container.
  A `:begin` / `:end` pair binds to the sibling nodes between its markers in
  one container. A dangling marker and a cross-container pair are refused.
- **GFM pipe tables**, refused when they start on the line after a paragraph
  line or are followed by a non-blank line in the same container.

## Addendum, 2026-10-14: frontmatter

The owner's decision of 2026-10-14: **frontmatter is allowed.** A leading YAML
block, opened by `---` on line 1 and closed by `---`, is opaque metadata. It is
not a block, has no leaves and takes no names. This settles the "after
frontmatter" in the partition rule above, which neither this document nor 0001
had defined. Without it, under the CommonMark profile, a YAML block's opening
`---` is a thematic break and its closing `---` a setext underline, which 0001
refuses.

**Line 2 must not be blank**, as pandoc reads a YAML metadata block, also
decided on 2026-10-14. A document whose line 1 is `---` and whose line 2 is
blank opens with a thematic break, not frontmatter, whatever `---` lines come
later. Without this, any document opening with a thematic break and holding a
later `---` line would turn its opening into metadata.

`conformance/cases/frontmatter/` pins the decision. The edges it does not
settle, and the reading taken for each (an unclosed block, `---` not on line
1, an empty block, and conflict markers inside one), are listed in
`conformance/cases/README.md`.

## Addendum, 2026-10-14: markers that name nothing, and three defaults

The owner's decisions of 2026-10-14.

**A marker must name a node.** The dangling-marker refusal of §3 widens from
"a one-line marker with no next sibling" to **a marker that names no node**.
Two more shapes now fall under it:

- an empty region, a `:begin` directly followed by its `:end`, with no
  sibling node between them;
- a one-line marker whose next sibling is another marker. A name binds to
  content, never to a marker, so stacking two markers does not make an alias.

Three defaults, decided the same day:

- **When duplicate-name and unpaired-region both apply, the refusal is
  duplicate-name.** A name is declared by a one-line marker or by a `:begin`.
  An `:end` closes a region and declares nothing. **dangling-marker is
  reported after both**: a document that also has a duplicate or unpaired
  name is refused for that.
- **Leaf content uses `\n` as its line ending everywhere**, code blocks
  included, whatever line endings the file uses.
- **Frontmatter is closed by a line of `---` followed only by spaces or
  tabs**, as pandoc reads a YAML metadata block, and never by YAML's `...`
  document end marker. The opening line is exactly `---`.

Two orders between refusals are fixed: the one above among the name
refusals, and `ambiguous-table` before `table-not-blank-above` (addendum on
ambiguous tables, below). Any other order is unspecified: a document to which
two refusals apply that neither fixes, such as a setext heading and an
indented code block, may be refused with either. A conformance case asserts
exactly one code, so it is written so that only one refusal applies to it, as
`conformance/cases/README.md` says, or combines only refusals whose order is
fixed here.

## Addendum, 2026-10-14: ambiguous tables

The owner's decision of 2026-10-14: an eleventh refusal, **`ambiguous-table`**,
for a table-like shape that GFM, as GitHub reads it, takes for a table and the
CommonMark-profile readers do not, or the reverse. It applies §6's rule that
the profile refuses an input two mature parsers draw differently.

Which shapes that covers, as widened by the owner's decision of 2026-10-15:
**a paragraph's last line, and the line under it in the same container, that
GitHub reads as a table header and delimiter row and that pandoc and
markdown-it do not both read as one.** GitHub's reading needs no pipe in
either line, and trims form feeds and vertical tabs from cells as well as
spaces and tabs. The reading pandoc and markdown-it share needs an unescaped
pipe in both lines, and trims spaces and tabs only. Either way, the header's
cells must be as many as the delimiter row's, and the delimiter row must not
already be a setext underline, a thematic break or a list item, which are
tried first. The shapes this refuses:

- a header line with no pipe over a one-cell delimiter row: `a` over `|---|`,
  `---|` or `:-:|`;
- a one-cell header line, with or without a pipe, over a delimiter row with
  no pipe that is not a setext underline: `a` over `:--`, `--:` or `:-:`,
  `| a |` or `a|` over `:--`;
- a delimiter row whose cells carry a form feed or a vertical tab, which stop
  `a` over `---` followed by a form feed from being a setext underline, and
  make `a | b` over `--- | ---` followed by a form feed a table to GitHub
  alone.

They are refused in a block quote and a list item as at top level. A line
that reaches its container only lazily is not under the paragraph's last
line in its container, so `> a` over an unprefixed `---` and a form feed is
not a table to any of the three, and is not refused. Where GitHub,
pandoc and markdown-it all read a table, it is a table. A one-cell header
over a delimiter row of two or more cells is a table to none of them, and is
not refused.

Where the shape also follows a non-blank line in its container, it is
`ambiguous-table`, not `table-not-blank-above`: the table exists in only one
of the readings.

The shapes 0002 §6 already names keep their own refusals. A non-blank line
directly after a table, which markdown-it reads as a row and pandoc as a
paragraph, is still `table-not-blank-below`.

Two more table edges, settled with this decision:

- **A row that is only `|`, with or without spaces around it, ends the
  table.** The line is then a non-blank line directly below the table, and
  is refused as `table-not-blank-below`. markdown-it reads it as an empty
  body row. pandoc's `gfm` reader and GitHub read the table followed by a
  paragraph `|`.
- **The table start is tried after every core block start**, as cmark-gfm
  tries its extensions. So `a | b` over `- | -` is a paragraph and a bullet
  list, not a table, as GitHub, pandoc's `gfm` reader and markdown-it all
  read it.

Probed with markdown-it-py 3.0.0 (preset `commonmark`, tables enabled),
pandoc 3.1.11.1 (`-f gfm`) and GitHub's `POST /markdown` in `gfm` mode.
