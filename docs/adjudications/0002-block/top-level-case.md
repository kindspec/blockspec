<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# blockspec#4: the case for (b)

A block is a top-level CommonMark node, and a list is one block.

Pins: kindspec/research `b292907` (the squash merge of PR #17,
`experiments/D8-block-definitions/`; only its `d2` rows differ from `8b9c33c`),
blockspec `1a969d0`, and corpus clones at the PRE-REGISTRATION-2 §6.2 pins.
`measure.py` printed `(pin)` for all seven arms. The new measurements are in
kindspec/research `experiments/D8-block-anchoring/cases/top-level/` (research main
`244dff0`)
(`edit_b_vs_d.py`, `rest.py`, `sizes.py`, `probe.py` and their `.txt`
output). They are new, not D8's, and they use D8's resolver
(`anchor_eval3.reanchor2`, hard policy) unchanged.

## Position

The block is (b): every top-level node. I argue (b) over (b2) because the
partition has to cover code and HTML too. Refusing low-entropy quotes is
already step 4's job in the resolver (D8 §7.3, H3), so the definition does
not need to do it. I concede one thing up front, and it is a big one. **If #4
only asks what stage 1 of a comment anchor resolves, my own measurement says
(d).** The argument below is that #4 asks more than that.

## 1. Duplicates and loud ambiguity

At ≥40 characters, `results.txt` "Summary, minlen=40", dup-in-file instances:

| arm | b | d | f |
|---|---|---|---|
| obsidian-help | 1.2% | 4.6% | 4.6% |
| k8s-l10n | 4.2% | 5.7% | 6.7% |
| cncf-toc | 0.7% | 1.0% | 1.3% |
| k8s-en | 2.1% | 2.1% | 2.3% |
| rust-book | 4.4% | 4.2% | 4.1% |

(b) is lowest or tied in six of seven arms. rust-book is the exception, and
its gap is 0.2–0.3 points: its top-level HTML captions and comments repeat at 24.0%
(By type, `b top-node / rust-book html`).
The list rows are the sharpest evidence. **A top-level list duplicates in-file
at 0.0% in obsidian-help (733 lists), against 9.0% for its items (1,990)**.
k8s-l10n is 8.7% against 13.1% (By type, `b … list` and `d … item`). Repeats are
procedure steps and parameter lines that recur across procedures, such as a
step that selects the import button a second time
(`measure.py --show d:obsidian-help`).

Content duplicates overstate loud ambiguity, because prefix and suffix context
separates many of them. So I measured the resolver itself, resolving every
top-level item of ≥40 characters against its own unchanged file (`rest.txt`).
These are loud refusals at rest:

| arm | items | (d) | (b), list then item |
|---|---|---|---|
| obsidian-help | 1,990 | 36 (1.81%) | 0 |
| k8s-en | 14,530 | 66 (0.45%) | 4 (0.03%) |
| cncf-toc | 14,584 | 40 (0.27%) | 0 |
| rust-book, site-policy, cmspec | 913 | 0 | 0 |

Item counts match `measure.py`'s `d … item` rows to within 2, which is the
generated-file filter. A larger unit that is unique is the better stage-1
scope while a document is at rest.

## 2. Under edits, where (d) wins and I concede it

D8 §3 measured edits only under D8's splitter (README, "What this does not
measure"). `edit_b_vs_d.py` re-runs §3.2's design over real history. It samples
top-level list items, applies the real edit `gap` commits later, and uses
anchor_eval2's line-oracle rule. It resolves the item two ways: as a block
under (d), and under (b) as the parent list (stage 1) and then the item inside
it (stage 2, with the same hard policy). Output is `edit-run.txt`:

| arm, gap | anchors | (b) correct / loud | (d) correct / loud |
|---|---|---|---|
| obsidian-help 5 | 1,018 | 95.2 / 4.8 | 97.9 / 2.1 |
| rust-book 5 | 324 | 92.3 / 7.7 | 99.7 / 0.3 |
| rust-book 25 | 125 | 92.8 / 7.2 | 100.0 / 0.0 |
| site-policy 5 | 594 | 96.0 / 4.0 | 97.5 / 2.5 |
| cncf-toc 25 | 72 | 91.7 / 8.3 | 100.0 / 0.0 |
| k8s-en 5 | 176 | 98.3 / 1.7 | 100.0 / 0.0 |

**Silent-wrong is 0 under both definitions in every arm.** (b) loses 0 (cmspec) to
8.3 points, all of them loud refusals. Nearly all of those are stage 1
refusing the edited list (`b stage1 refused=40` against `stage2 refused=2` in
rust-book gap 5). An edit to item 4 changes the stage-1 quote of a comment on
item 1. Where the two disagree, (d) wins most cases. In obsidian gap 5, (d) is
right and (b) is loud 39 times, and the reverse happens 11 times; those 11 are
§1's ambiguity cases. A second structural cost, from `probe.py`: changing one
bullet character (`-` to `*`) mid-list splits it into two top-level lists. That
changes (b)'s partition and leaves (d)'s items alone.

D8's own §3.2 silent-wrongs in list items (a rust-book TOC line and an
obsidian procedure, D8 lines 504–510) came from the **naive** policy. The hard
policy made none, and neither did it here. That evidence does not favour (b),
and I do not claim it.

## 3. What a comment or suggestion attaches to

A comment attaches to a **span**, not to a block. D8 §3.4 and §7.3 make the
block stage 1 only: a search scope that rules out lookalikes elsewhere in the
file (two-stage: 0.00% silent-wrong against one-stage's 15.34% at gap 25).
What stage 1 needs is a scope that is unique and still found after edits. §1
shows (b) is the more unique scope, and §2 shows (d) is the more durable one.
Lists are small, so (b) does not lose precision. The median top-level list has
3 items and 208, 289 and 330 characters in obsidian-help, rust-book and k8s-en
(`sizes.py`, all tracked files). That is the size of a paragraph. On
sidecar size I concede that `block.exact` (D8 §7.3) stores the whole list,
and the p90 list is 540 to 1,092 characters.

A suggestion that reorders, inserts or deletes items is one block replacement
under (b). Under (d) it is an edit that spans several blocks or falls between
them. This is argued, not measured.

## 4. Where (b) is right and (d) has no answer

These are the parts of #4 that are not stage-1 anchoring:

- **A (b) block renders from its own bytes. A (d) item does not.** CommonMark
  makes a list loose if any of its items are separated by a blank line.
  `probe.py` shows that one blank line before item 3 wraps items 1 and 2 in
  `<p>` as well. A transcluded item's rendering therefore depends on siblings
  that the transclusion leaves out. (Link reference definitions are global,
  and they hit both definitions alike.)
- **(d) cannot be named without a new rule.** 0001-syntax says
  `<!-- #name -->` binds to the next sibling node. In `probe.py`, a marker at
  column 0 between two items ends the list and makes three top-level nodes.
  The same marker indented inside item 1 becomes item 1's last child, so it
  has no next sibling. Written first inside an item, it binds to the item's
  paragraph, not the item. Under (b) a marker before a list names the list
  with the rule 0001 already wrote. Under (d), blockspec has to add an
  item-binding rule and its conformance cases.
- **The partition is flat.** Under (b), every non-blank line outside the
  frontmatter belongs to exactly one block. The only exceptions are link
  reference definitions (README, `uncovered`). (d) is also a partition, but
  (d2) nests and (f) drops list and quote markers from every block.

## 5. Implementation and conformance cost

I concede that (b) does not save any parsing. Finding where a list ends
requires CommonMark's list-item rules, which have 48 examples ("List items")
plus 26 more ("Lists") in 0.31.2 (D5 §1, spec.json). Any conforming splitter
pays that cost under either definition. The difference is in blockspec's own
cases. (d) adds item identity under renumbering, nested items, items with
several paragraphs, and the marker-binding rule above. (b) adds the
bullet-change split and the column-0 marker split, and (d) needs those as well.
These cases are listed, not counted.

## 6. Reversal cost after draft 0

The cost is low either way, and that cuts both ways. Nothing is written into
the authored file under either definition (D8 §7.1, brief §1: no minted ids).
Every stored anchor carries `base`, the blob SHA (D8 §7.3), so a migration can
re-cut each `block.exact` from the base blob under the new definition. That is
mechanical, and git already holds the input. What does change is the spec text,
the conformance cases and any third-party resolver. Neither definition reverses
blockspec#3: 0001 "What would reverse it" item 2 says both are CommonMark tree
nodes.

## Recommendation, and what would change it

Adopt (b) as the block: the unit that is partitioned, named, transcluded and
listed in the conformance suite. **Do not tie stage 1 of the anchor to it for
list content.** Let stage 1 resolve the smallest enclosing list item when the
quoted span lies inside one. §2 measured that at +1.5 to +8.3 points of
correct resolution, with no silent-wrong cost. §1's ambiguity cost is real but
smaller, at 0 to 1.81% at rest. In other words, I concede the anchoring half
to (d) and hold the identity, naming and transclusion half for (b).

The deciding question is: **does blockspec need to transclude or name a single
list item?** If it does, §4's two problems (rendering that depends on siblings,
and binding a marker to an item) have to be solved under any definition, and
(d) costs little more than (b). If it does not, (b) is the smaller spec, and
§2 is solved inside the resolver without redefining the block.
