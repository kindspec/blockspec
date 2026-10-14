<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# blockspec#4: a block is a leaf node of the CommonMark tree

**Position.** Definition **(f)** from research PR #17
(`experiments/D8-block-definitions`, squash-merged as `b292907`; only its
`d2` rows differ from the PR head `8b9c33c`). A block is every
paragraph, heading, code block, HTML block, table or thematic break, at any
depth. A list item's paragraphs are blocks. The list, the item and the block
quote are containers, not blocks. Over (d2): not a partition, since a parent
item contains its sub-items.
Over (d): it stops at the top level, so a nested step stays inside its parent.

Short version: (b) has fewer duplicates. That edge is about 0.3 points, and every
case of it is loud. (f) matches what a comment, a suggestion or a marker
actually points at. It keeps stage 1 on the exact-match path when someone edits
a neighbouring item. It is also the only one of the two that can later be
coarsened without losing anything.

## 1. Duplicates and loud ambiguity: (b) wins, narrowly

At minlen 40 I pooled the seven arms from `results.txt` (the script is in the
command note at the end):

| def | instances dup in file | distinct, dup in file | local, dup in file |
|---|---|---|---|
| b | 7571/226022 = 3.35% | 1587/200944 = 0.79% | 1202/194004 = 0.62% |
| f | 14523/290897 = 4.99% | 2785/252660 = 1.10% | 2223/242644 = 0.92% |
| b, without k8s-l10n | 1.88% | 0.53% | 0.48% |
| f, without k8s-l10n | 2.15% | 0.76% | 0.69% |

**Concession.** (f) duplicates more, and the gap is real. It shows up in
obsidian-help: paragraphs at any depth duplicate at 4.6%, against 1.0% for
top-level paragraphs, and (b)'s 733 lists show 0 duplicates (`results.txt`, "By
type, minlen=40").

What the duplicates are. `measure.py --show f:obsidian-help` at the pins gives
232 instances and 89 distinct contents. Most of them are procedure steps: the step
that opens the command palette with its keyboard shortcut appears 6 times in one
file, and the step that selects the community plugins entry in the side menu 4
times. That is a step that recurs within one file. It is not a template.

Why the gap costs little:

- **Duplicates are not silent.** The brief §1 says ambiguity is "detectable at
  resolve time". A second exact match is a loud `#REF!`, and that holds under
  every definition.
- **Context settles most duplicates.** D8 §7.3 step 3 uses prefix and suffix to
  choose between exact matches. In the edit runs of §3, exact matches that stayed
  ambiguous after context (`AMBIGUOUS`) were 0.0–0.3% of in-list anchors under
  (f).
- **(b) hides duplicates rather than removing them.** The repeated step is still
  repeated. Under (b) it lives inside a unique list, so stage 2 (span within
  block) meets it instead. Exactly where that cost lands depends on the span
  algorithm, and I did not measure it.

## 2. What a comment or suggestion attaches to

Reviewers comment on a step, a bullet or a sentence. They do not comment on "the
list". Three facts from the corpora and the decided design point this way:

- **D8 §3.4's measured design** is that a span "may only be searched inside the
  block stage 1 resolved". Under (b), a comment on one bullet stores the whole
  list as `block.exact` (D8 §7.3's `comments.yaml` shape). In obsidian-help the
  enclosing list is a median 3.9× and p90 13.2× the length of the paragraph
  anchored inside it (`edits.py`, gap 1). Every comment and suggestion on one
  item then carries a copy of the whole list.
- **Region markers.** Adjudication 0001's probe shows
  `marker inside a list item -> … paragraph,
  html_block, paragraph`. The marker "binds to the next sibling". Under (f) that
  sibling is a block. Under (b) it is not a block, so (b) has two options: forbid
  markers inside lists, or add a second unit of identity.
- **Transclusion.** Transcluding one policy bullet or one procedure step needs a
  named target (D8 §8.1 R2). Under (b), the smallest addressable thing inside a
  list is the whole list.

**Concession.** A selection across three bullets is one block under (b) and a
range of leaves under (f). But a selection across two top-level paragraphs is a
range under (b) too. Range anchors are needed under both definitions, so (b) does
not avoid them.

## 3. Behaviour under edits (D8 §3)

D8 §3.1–3.2 measured edits only under D8's splitter (README, "What this does not
measure"). I ran D8's own hardened resolver, `anchor_eval3.reanchor2(hard=True)`,
under both definitions. The anchors were the paragraphs of ≥40 characters inside
a top-level list, each unique at the anchoring version, compared at file-version
gap G. Under (b) the anchored block is the enclosing list. Under (f) it is the
paragraph. Script: kindspec/research
`experiments/D8-block-anchoring/cases/leaf/edits2.py` (PR #18, `18506e9`).

| arm | G | anchors | (b) EXACT | (b) FUZZY | (b) resolves | (f) EXACT | (f) FUZZY | (f) resolves |
|---|---|---|---|---|---|---|---|---|
| obsidian-help | 1 | 20690 | 83.3% | 13.9% | 97.2% | 95.1% | 2.5% | 97.6% |
| obsidian-help | 5 | 14331 | 54.0% | 32.7% | 86.7% | 81.5% | 8.2% | 89.8% |
| obsidian-help | 25 | 1737 | 6.4% | 48.2% | 54.6% | 35.3% | 18.7% | 54.1% |
| rust-book | 5 | 11018 | 36.7% | 52.5% | 89.2% | 79.9% | 11.4% | 91.3% |
| rust-book | 25 | 5508 | 4.2% | 54.5% | 58.7% | 43.5% | 28.7% | 72.2% |

"Resolves" counts EXACT, EXACT_CTX and FUZZY. "Exact" is stage 1's exact-match
step, D8 §7.3 step 2.

What this shows:

- **(b) pushes edits onto the fuzzy path.** Any edit to any item changes the
  list's bytes. At gap 5, 33–53% of (b)'s anchors resolve only by fuzzy match,
  against 8–11% under (f). D8 §3.2 found that silent wrongs concentrate in
  fuzzy, low-entropy matches. (f) keeps 80–82% of these anchors on the exact
  path, where (b) keeps 37–54%.
- **Total recall is close, except at depth.** (f) leads by 0.4 to 3 points at
  gaps 1 and 5, and by 13.5 at rust-book gap 25, where 40.4% of (b)'s anchors
  orphan against 13.9% of (f)'s. At obsidian gap 25, (b) leads by 0.5.
  **Concession:** that is one arm, not a general recall advantage. Its losses
  are loud refusals: low entropy at 0.5–4.7%, margin
  at 0.8–11.1%. On short items that is the trade D8 §3.2 asks for.
- **The two definitions disagree on 0.1–3.1% of anchors.** Both resolve, but the
  leaf (f) finds is not inside the list (b) finds. One of them is wrong, or the
  item moved to another list. I have no oracle here, so I make no claim about
  which. That is the next measurement: run blockspec's TLLC oracle on these
  pairs.
- Under (f), exact match does not prove correct. Spike LOG §35's FOUND (at
  `1a969d0`) is an exact, unique match on moved text, and 0001 tallies its Q
  records as 76 heading, 64 prose and 3 list. **Concession:** smaller blocks make
  that coincidence more likely. The spike's units were D8 blank-line chunks, so it
  does not separate (b) from (f).

## 4. Implementation and conformance cost

**Concession, the strongest point for (b).** A top-level node is a contiguous
line range, so "block content = source lines, stripped" falls out for free. A
nested leaf's content needs the container prefixes removed: indentation, `>`,
lazy continuation lines, tabs inside items. That is a spec clause plus
conformance cases (nested quote in list, lazy continuation, tab expansion),
perhaps 10 to 20 cases. This is an estimate, not a measurement.

**Where (b) saves less than it looks.**

- Finding where a top-level list ends already requires CommonMark's list-item
  rules: "List items" (48 examples) and "Lists" (26) (D5 §1). (b) parses items
  either way and then throws them away.
- `measure.py` extracts (f) with six `out["f"]` appends inside the same token
  loop that does (b).
- CommonMark already defines a paragraph's content with container prefixes
  removed, so the clause can cite the spec. blockspec need not invent it.
- 0001's reversal item 2 is not triggered: both are CommonMark tree nodes.

## 5. Reversal cost after draft 0

The cost is asymmetric, and it favours starting fine:

- **f → b is lossless.** A stored leaf anchor finds its leaf, and the leaf's
  top-level ancestor is computable. A migration can rewrite every sidecar
  mechanically.
- **b → f is lossy.** A block-level comment or suggestion on a list, with no
  span, does not say which item it meant. Neither does a marker convention that
  never bound inside lists. The migration needs a human, or it guesses, and a
  guess is a silent wrong.

Draft 0 fixes the anchor format in sidecars that will hold the first product's
comments. The definition that can be coarsened later is the cheaper bet.

## Where (b) is right

Fewer duplicates (0.62% against 0.92% local, pooled), raw-byte content, and a
multi-item selection as one block. None changes the recommendation: the first
is loud and small, the second costs one clause, the third needs range anchors
under both definitions anyway.

**What would change my mind:** an oracle-graded run of the §3 pairs showing (b)'s
fuzzy list matches are correct where (f)'s exact leaf matches are wrong, at a
rate above (f)'s 0.3-point duplicate penalty.

## Commands

- Pooled table: `results.txt` "Summary, minlen=40", each column summed over
  the seven arms per definition.
- `python3 -I measure.py --clone … --show f:obsidian-help` against clones at the
  README pins. All seven were at
  their pins with no tracked changes (`git rev-parse`, `git status
  --porcelain -uno`).
- `python3 -I edits.py obsidian-help/obsidian-help 'en/*.md' G 176` and
  `edits2.py`, in kindspec/research `experiments/D8-block-anchoring/cases/leaf/`,
  with `D8-identity/` at research `b292907`. Output is `edits.txt` and
  `edits2.txt` beside them. Files were
  shuffled with seed 7. Version pairs follow each file's own `git log`. A block's
  offset is the start of its first line, an approximation for nested
  paragraphs.
